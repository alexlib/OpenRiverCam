import os
import OpenRiverCam
import utils
import logging
import io
import cv2
import numpy as np
import requests
from datetime import datetime, timedelta
from shapely.geometry import shape
from rasterio.plot import reshape_as_raster


def upload_file(fn, bucket, dest=None, logger=logging):
    """
    Uploads BytesIO obj representation of data in file 'fn' in bucket

    :param fn: str, full local path to file containing movie
    :param bucket: str, name of bucket, if it does not exist, it will be created
    :param dest=None: str, name of file in bucket, if left as None, the file name is stripped from fn
    :param logger=logging: logger-object
    :return: None
    """
    if dest is None:
        dest = os.path.split(os.path.abspath(fn))[1]
    s3 = utils.get_s3()

    # Create bucket if it doesn't exist yet.
    if s3.Bucket(bucket) not in s3.buckets.all():
        s3.create_bucket(Bucket=bucket)
    s3.Bucket(bucket).upload_file(fn, dest)
    logger.info(f"{fn} uploaded in {bucket}")


def extract_frames(movie, prefix="frame", logger=logging):
    """
    Extract raw frames, only lens correct using camera lensParameters, and store in RGB photos

    :param movie: dict containing movie information
    :param camera: dict, camera properties, such as lensParameters, name
    :param prefix="frame": str, prefix of file names, used in storage bucket, normally not changed by user
    :param logger=logging: logger-object
    :return: None
    """
    # open S3 bucket
    s3 = utils.get_s3()
    n = 0
    logger.info(
        f"Writing movie {movie['file']['identifier']} to {movie['file']['bucket']}"
    )
    # open file from bucket in memory
    bucket = movie["file"]["bucket"]
    fn = movie["file"]["identifier"]
    # make a temporary file
    s3.Bucket(bucket).download_file(fn, fn)
    for _t, img in OpenRiverCam.io.frames(
        fn, lens_pars=movie["camera_config"]["camera_type"]["lensParameters"]
    ):
        # filename in bucket, following template frame_{4-digit_framenumber}_{time_in_milliseconds}.jpg
        dest_fn = "{:s}_{:04d}_{:06d}.jpg".format(prefix, n, int(_t * 1000))
        logger.debug(f"Write frame {n} in {dest_fn} to S3")
        # encode img
        ret, im_en = cv2.imencode(".jpg", img)
        buf = io.BytesIO(im_en)
        # Seek beginning of bytestream
        buf.seek(0)
        # Put file in bucket
        s3.Object(bucket, dest_fn).put(Body=buf)
        n += 1
    # clean up of temp file
    os.remove(fn)

    # API request to confirm frame extraction is finished.
    requests.post("http://portal/api/processing/extract_frames/%s" % movie["id"])


def extract_project_frames(movie, prefix="proj", logger=logging):
    """
    Extract frames, lens correct, greyscale correct and project to defined AOI with GCPs, water level and camera position
    Results in GeoTIFF files in desired projection and resolution within bucket defined in movie

    :param movie: dict, movie information
    :param prefix="proj": str, prefix of file names, used in storage bucket, normally not changed by user
    :param logger=logging: logger-object
    :return: None
    """
    # open S3 bucket
    camera_config = movie["camera_config"]
    s3 = utils.get_s3()
    n = 0
    logger.info(
        f"Writing movie {movie['file']['identifier']} to {movie['file']['bucket']}"
    )
    # open file from bucket in memory
    bucket = movie["file"]["bucket"]
    fn = movie["file"]["identifier"]
    # make a temporary file
    s3.Bucket(bucket).download_file(fn, fn)
    for _t, img in OpenRiverCam.io.frames(
        fn, lens_pars=camera_config["camera_type"]["lensParameters"]
    ):
        # filename in bucket, following template frame_{4-digit_framenumber}_{time_in_milliseconds}.jpg
        dest_fn = "{:s}_{:04d}_{:06d}.tif".format(prefix, n, int(_t * 1000))
        logger.debug(f"Write frame {n} in {dest_fn} to S3")
        bbox = shape(
            camera_config["aoi"]["bbox"]["features"][0]["geometry"]
        )  # extract the one and only geometry from geojson
        # reproject frame with camera_config
        # inputs needed
        corr_img, transform = OpenRiverCam.cv.orthorectification(
            img=img,
            lensPosition=camera_config["lensPosition"],
            h_a=movie["h_a"],
            bbox=bbox,
            resolution=0.01,
            **camera_config["gcps"],
        )
        raster = reshape_as_raster(corr_img)
        # write to temporary file
        OpenRiverCam.io.to_geotiff(
            "temp.tif",
            raster,
            transform,
            crs=camera_config["site"]["crs"],
            compress="deflate",
        )
        # Put file in bucket
        s3.Bucket(bucket).upload_file("temp.tif", dest_fn)
        n += 1
    # finally write last frame as .jpg for front end and write geotransform as .csv
    dest_fn = "reprojection_preview.jpg"
    trans_fn = "reprojection_preview.transform"  # file name for geotransform
    ret, im_en = cv2.imencode(".jpg", corr_img)
    buf = io.BytesIO(im_en)
    # Seek beginning of bytestream
    buf.seek(0)
    # Put file in bucket
    s3.Object(bucket, dest_fn).put(Body=buf)
    # write the geotransform
    buf = io.BytesIO(str(transform).encode())
    buf.seek(0)
    s3.Object(bucket, trans_fn).put(Body=buf)
    # clean up of temp file
    os.remove(fn)
    logger.info(f"{fn} successfully reprojected into frames in {bucket}")


def get_aoi(camera_config, logger=logging):
    """
    add the aoi dictionary to camera_config based on user inputs

    :param camera_config: camera configuration with ["aoi"]["bbox"] still missing
    :param logger=logging: logger-object
    :return: None
    """
    # some assertion
    if not "gcps" in camera_config:
        logger.error(
            "'gcps' key missing in camera_config dictionary. User must first specify ground control points in interface."
        )
    if not "corners" in camera_config:
        logger.error(
            "'corners' key missing in camera_config dictionary. User must first specify a box in the camera objective"
        )
    if not "site" in camera_config:
        logger.error(
            "'site' key missing in camera_config dictionary. User must first specify site id, location and crs"
        )
    gcps = camera_config["gcps"]
    corners = camera_config["corners"]
    crs = f"EPSG:{camera_config['site']['crs']}"
    bbox = OpenRiverCam.cv.get_aoi(gcps["src"], gcps["dst"], corners)
    bbox_json = OpenRiverCam.io.to_geojson(bbox, crs=crs)
    logger.debug(f"bbox: {bbox_json}")
    # return bbox in case called from direct request
    return bbox_json


def compute_piv(movie, prefix="proj", piv_kwargs={}, logger=logging):
    """
    compute velocities over frame pairs, choosing frame interval, start / end frame.

    :param movie: dict, contains file dictionary and camera_config
    :param prefix: str, prefix of geotiff files assumed to be present in bucket
    :param piv_kwargs: str, arguments passed to piv algorithm, parameters are defined in docstring of
           openpiv.pyprocess.extended_search_area_piv
    :param logger: logger object
    :return: None
    """
    var_names = ["v_x", "v_y", "s2n", "corr"]
    var_attrs = [
        {
            "standard_name": "sea_water_x_velocity",
            "long_name": "Flow element center velocity vector, x-component",
            "units": "m s-1",
            "coordinates": "lon lat",
        },
        {
            "standard_name": "sea_water_y_velocity",
            "long_name": "Flow element center velocity vector, y-component",
            "units": "m s-1",
            "coordinates": "lon lat",
        },
        {
            "standard_name": "ratio",
            "long_name": "signal to noise ratio",
            "units": "",
            "coordinates": "lon lat",
        },
        {
            "standard_name": "correlation_coefficient",
            "long_name": "correlation coefficient between frames",
            "units": "",
            "coordinates": "lon lat",
        },
    ]
    encoding = {var: {"zlib": True} for var in var_names}
    start_time = datetime.strptime(movie["timestamp"], "%Y-%m-%dT%H:%M:%SZ")
    resolution = movie["camera_config"]["resolution"]
    # open S3 bucket
    camera_config = movie["camera_config"]
    s3 = utils.get_s3()
    n = 0
    logger.info(
        f"Computing velocities from projected frames in {movie['file']['bucket']}"
    )
    # open file from bucket in memory
    bucket = movie["file"]["bucket"]
    # get files with the right prefix
    fns = s3.Bucket(bucket).objects.filter(Prefix=prefix)
    frame_b = None
    ms = None
    time, v_x, v_y, s2n, corr = [], [], [], [], []

    for n, fn in enumerate(fns):
        # store previous time offset
        _ms = ms
        # determine time offset of frame from filename
        ms = timedelta(milliseconds=int(fn.key[-10:-4]))
        frame_a = frame_b
        buf = io.BytesIO()
        fn.Object().download_fileobj(buf)
        buf.seek(0)
        frame_b = OpenRiverCam.piv.imread(buf)
        # rewind to beginning of file
        if (frame_a is not None) and (frame_b is not None):
            # we have two frames in memory, now estimate velocity
            logger.debug(f"Processing frame {n}")
            # determine time difference dt between frames
            dt = (ms - _ms).total_seconds()
            cols, rows, _v_x, _v_y, _s2n, _corr = OpenRiverCam.piv.piv(
                frame_a,
                frame_b,
                res_x=resolution,
                res_y=resolution,
                dt=dt,
                **piv_kwargs,
            )
            v_x.append(_v_x), v_y.append(_v_y), s2n.append(_s2n), corr.append(_corr)
            time.append(start_time + ms)
    # finally read GeoTiff transform from the first file
    for fn in fns.limit(1):
        logger.info(f"Retrieving coordinates of grid from {fn.key}")
        buf = io.BytesIO()
        fn.Object().download_fileobj(buf)
        buf.seek(0)
        xs, ys, lons, lats = OpenRiverCam.io.convert_cols_rows(buf, cols, rows)

    # prepare local axes
    spacing_x = np.diff(cols[0])[0]
    spacing_y = np.diff(rows[:, 0])[0]
    x = np.linspace(
        resolution / 2 * spacing_x,
        (len(cols[0]) - 0.5) * resolution * spacing_x,
        len(cols[0]),
    )
    y = np.flipud(
        np.linspace(
            resolution / 2 * spacing_y,
            (len(rows[:, 0]) - 0.5) * resolution * spacing_y,
            len(rows[:, 0]),
        )
    )

    # prepare dataset
    dataset = OpenRiverCam.io.to_dataset(
        [v_x, v_y, s2n, corr],
        var_names,
        x,
        y,
        time=time,
        lat=lats,
        lon=lons,
        xs=xs,
        ys=ys,
        attrs=var_attrs,
    )
    # write to file and to bucket
    dataset.to_netcdf("temp.nc", encoding=encoding)
    s3.Bucket(bucket).upload_file("temp.nc", "velocity.nc")
    os.remove("temp.nc")
    logger.info(f"velocity.nc successfully written in {bucket}")


def compute_q(
    movie, v_corr=0.85, quantile=[0.05, 0.25, 0.5, 0.75, 0.95], logger=logging
):
    """
    compute velocities over provided bathymetric cross section points, depth integrated velocities and river flow
    over several quantiles.

    :param movie: dict, contains file dictionary and camera_config
    :param v_corr: float (range: 0-1, typically close to 1), correction factor from surface to depth-average
           (default: 0.85)
    :param quantile: float or list of floats (range: 0-1)  (default: 0.5)
    :return: None
    """
    encoding = {}
    # open S3 bucket
    s3 = utils.get_s3()
    logger.info(
        f"Extracting cross section from velocities in {movie['file']['bucket']}"
    )
    # open file from bucket in memory
    bucket = movie["file"]["bucket"]
    fn = "velocity_filter.nc"
    s3.Bucket(bucket).download_file(fn, "temp.nc")

    # retrieve velocities over cross section only (ds_points has time, points as dimension)
    ds_points = OpenRiverCam.io.interp_coords(
        "temp.nc", *zip(*movie["bathymetry"]["coords"])
    )

    # add the effective velocity perpendicular to cross-section
    ds_points["v_eff"] = OpenRiverCam.piv.vector_to_scalar(
        ds_points["v_x"], ds_points["v_y"]
    )

    # integrate over depth with vertical correction
    ds_points["q"] = OpenRiverCam.piv.depth_integrate(
        ds_points["zcoords"],
        ds_points["v_eff"],
        movie["camera_config"]["gcps"]["z_0"],
        movie["h_a"],
        v_corr=v_corr,
    )

    # integrate over the width of the cross-section
    Q = OpenRiverCam.piv.integrate_flow(ds_points["q"], quantile=quantile)

    # extract a callback from Q
    Q_dict = {
        "discharge_q{:02d}".format(int(float(q) * 100)): float(Q.sel(quantile=q))
        for q in Q["quantile"]
    }

    # overwrite gridded netCDF with cross section netCDF
    ds_points.to_netcdf("temp.nc", encoding=encoding)
    s3.Bucket(bucket).upload_file("temp.nc", "q_depth.nc")
    logger.info(f"q_depth.nc successfully written in {bucket}")

    # overwrite gridded netCDF with cross section netCDF
    Q.to_netcdf("temp.nc", encoding=encoding)
    s3.Bucket(bucket).upload_file("temp.nc", "Q.nc")

    os.remove("temp.nc")
    logger.info(f"Q.nc successfully written in {bucket}")
    return Q_dict


def filter_piv(
    movie, filter_temporal_kwargs={}, filter_spatial_kwargs={}, logger=logging
):
    """
    Filters a PIV velocity dataset (derived with compute_piv) with several temporal and spatial filter. This removes
    noise, isolated velocities in space and time, and moving features that are not likely to be water related.
    Input keyword arguments to the filters can be provided in the request, through several dictionaries.

    :param movie: dict, contains file dictionary and camera_config
    :param filter_temporal_kwargs: dict with the following possible kwargs for temporal filtering
        (+default values if not provided):
        kwargs_angle, dict, containing the following keyword args:
            angle_expected=0.5 * np.pi -- expected angle in radians of flow velocity measured from upwards, clock-wise.
                In OpenRiverCam this is always 0.5*pi because we make sure water flows from left to right
            angle_bounds=0.25 * np.pi -- the maximum angular deviation from expected angle allowed. Velocities that are
                outside this bound are masked
        kwargs_std, dict, containing following keyword args:
            tolerance=1.0 -- maximum allowed std/mean ratio in a pixel. Individual time steps outside this ratio are
                filtered out.
        kwargs_velocity, dict, containing following keyword args:
            s_min=0.1 -- minimum velocity expected to be measured by piv in m/s. lower velocities per timestep are
                filtered out
            s_max=5.0 -- maximum velocity expected to be measured by piv in m/s. higher velocities per timestep are
                filtered out
        kwargs_corr, dict, containing following keyword args:
            corr_min=0.4 -- minimum correlation needed to accept a velocity on timestep basis. Le Coz in FUDAA-LSPIV
                suggest 0.4
        kwargs_neighbour, dict, containing followiung keyword args:
            roll=5 -- amount of time steps in rolling window (centred)
            tolerance=0.5 -- Relative acceptable velocity of maximum found within rolling window

    :param filter_spatial_kwargs: dict with the following possible kwargs for spatial filtering
        (+default values if not provided):
        kwargs_nan, dict, containing following keyword args:
            tolerance=0.8 -- float, amount of NaNs in search window measured as a fraction of total amount of values
                [0-1]
            stride=1 --int, stride used to determine relevant neighbours
        kwargs_median, dict, containing following keyword args:
            tolerance=0.7 -- amount of standard deviations tolerance
            stride=1 -- int, stride used to determine relevant neighbours

    :param logger: logging object
    :return:
    """

    # open S3 bucket
    s3 = utils.get_s3()
    logger.info(f"Filtering surface velocities in {movie['file']['bucket']}")
    # open file from bucket in memory
    bucket = movie["file"]["bucket"]
    fn = "velocity.nc"
    s3.Bucket(bucket).download_file(fn, "temp.nc")
    logger.debug("applying temporal filters")
    ds = OpenRiverCam.piv.filter_temporal("temp.nc", **filter_temporal_kwargs)
    logger.debug("applying spatial filters")
    ds = OpenRiverCam.piv.filter_spatial(ds, **filter_spatial_kwargs)

    # remove original file
    os.remove("temp.nc")
    encoding = {var: {"zlib": True} for var in ds}
    # write gridded netCDF with filtered velocities netCDF
    ds.to_netcdf("temp.nc", encoding=encoding)
    s3.Bucket(bucket).upload_file("temp.nc", "velocity_filter.nc")
    os.remove("temp.nc")
    logger.info(f"velocity_filter.nc successfully written in {bucket}")


def run(movie, piv_kwargs={}, logger=logging):
    """
    Execute steps of project frames, compute_piv, filter_piv and compute_q.

    :param movie: dict, movie information
    :param logger=logging: logger-object
    :return: None
    """

    extract_project_frames(movie, logger=logger)
    compute_piv(movie, piv_kwargs=piv_kwargs, logger=logger)
    filter_piv(movie, logger=logger)
    Q = compute_q(movie, logger=logger)
    # TODO: Return the discharge value in the processing callback to be stored in the database.
    logger.debug(f"Performing callback with discharge value {Q}")
    # API request to confirm movie run is finished.
    requests.post(
        "http://portal/api/processing/run/%s" % movie["id"],
        json=Q,
    )
    logger.info(f"Full run succesfull for movie {movie['id']}")


def run_camera_config(movie, logger=logging):
    """
    Execute steps of get_aoi and extract_project_frames.

    :param movie: dict, movie information
    :param logger=logging: logger-object
    :return: None
    """

    bbox_json = get_aoi(movie['camera_config'], logger=logger)
    movie['camera_config']['aoi']['bbox'] = bbox_json
    extract_project_frames(movie, logger=logger)

    requests.post(
        "http://portal/api/processing/get_aoi/{:d}".format(movie['camera_config']["id"]),
        json=bbox_json,
    )
    logger.info(f"Camera config run succesfull for configuration {movie['camera_config']['id']}")