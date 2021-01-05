import os
import OpenRiverCam
import utils
import logging
import io
import cv2
from shapely.geometry import shape
from rasterio.plot import reshape_as_raster


def upload_file(fn, bucket, dest=None, logger=logging):
    """
    Uploads BytesIO obj representation of data in file 'fn' in bucket
    :param fn: str, full local path to file containing movie
    :param bucket: str, name of bucket, if it does not exist, it will be created
    :param dest=None: str, name of file in bucket, if left as None, the file name is stripped from fn

    :return:
    """
    if dest is None:
        dest = os.path.split(os.path.abspath(fn))[1]
    s3 = utils.get_s3()

    # Create bucket if it doesn't exist yet.
    if s3.Bucket(bucket) not in s3.buckets.all():
        s3.create_bucket(Bucket=bucket)
    s3.Bucket(bucket).upload_file(fn, dest)
    logger.info(f"{fn} uploaded in {bucket}")


def extract_frames(movie, camera, prefix="frame", logger=logging):
    """
    Extract raw frames, only lens correct using camera lensParameters, and store in RGB photos
    :param movie: dict containing movie information
    :param camera: dict, camera properties, such as lensParameters, name
    :param prefix: str, prefix of file names, used in storage bucket
    :param logger:
    :return:
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
    for _t, img in OpenRiverCam.io.frames(fn, lens_pars=camera["lensParameters"]):
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
    # TODO: Post status code on specific end point (Rick)
    # requests.post("http://.....", msg)
    return 200


def extract_project_frames(movie, prefix="proj", logger=logging):
    """
    Extract frames, lens correct, greyscale correct and project to defined AOI with GCPs, water level and camera position
    Results in GeoTIFF files in desired projection and resolution within bucket defined in movie
    :param movie: dict, movie information
    :param prefix="proj": str, prefix of file names, used in storage bucket
    :param logger=logging: logging obj
    :return:
    """
    # TODO check on time frame of movie and validity of the camera_config
    # TODO check if aoi is defined, without it, projection is not possible
    # TODO check if gcps are defined, without it projection not possible
    # TODO check resolution, without set resolution, not possible to reproject
    # TODO reprojection implementation based on AOI object and resolution
    # TODO storage in BytesIO representation of GeoTIFF (rasterio) and push to bucket

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
    # clean up of temp file
    os.remove(fn)
    logger.info(f"{fn} sucessfully reprojected into frames in {bucket}")
    # TODO: Post status code on specific end point (Rick)
    # requests.post("http://.....", msg)
    return 200

def get_aoi(camera_config, logger=logging):
    """

    :param camera_config: camera configuration with ["aoi"]["bbox"] still missing
    :return:
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
    logger.debug("bbox: {bbox_json}")
    if not "aoi" in camera_config:
        camera_config["aoi"] = {}
    camera_config["aoi"]["bbox"] = bbox_json
    logger.info("Bounding box of aoi derived")
    # TODO replace return for a requests.post
    return camera_config


def compute_piv(movie, file, prefix="proj", piv_kwargs={}, logger=logging):
    """
    compute velocities over frame pairs, choosing frame interval, start / end frame.

    :return:
    """
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
    for n, fn in enumerate(fns.limit(3)):
        frame_a = frame_b
        buf = io.BytesIO()
        fn.Object().download_fileobj(buf)
        buf.seek(0)
        frame_b = OpenRiverCam.piv.imread(buf)
        # rewind to beginning of file
        if (frame_a is not None) and (frame_b is not None):
            # we have two frames in memory, now estimate velocity
            logger.info(f"Processing frame {n}")
            cols, rows, v_x, v_y, s2n = OpenRiverCam.piv.piv(frame_a, frame_b, **piv_kwargs)
        print("Check")

    # finally read GeoTiff transform from the first file
    for fn in fns.limit(1):
        logger.info("Retrieving axis information")
        buf = io.BytesIO()
        fn.Object().download_fileobj(buf)
        buf.seek(0)
        lons, lats = OpenRiverCam.io.convert_cols_rows(buf, cols, rows)
    encoding = {var: {"zlib": True} for var in var_names}


    #     for _t, img in OpenRiverCam.io.frames(
    #         fn, lens_pars=camera_config["camera_type"]["lensParameters"]
    #     ):
    #     # filename in bucket, following template frame_{4-digit_framenumber}_{time_in_milliseconds}.jpg
    #     dest_fn = "{:s}_{:04d}_{:06d}.tif".format(prefix, n, int(_t * 1000))
    #     logger.debug(f"Write frame {n} in {dest_fn} to S3")
    #     bbox = shape(
    #         camera_config["aoi"]["bbox"]["features"][0]["geometry"]
    #     )  # extract the one and only geometry from geojson
    #     # reproject frame with camera_config
    #     # inputs needed
    #     corr_img, transform = OpenRiverCam.cv.orthorectification(
    #         img=img,
    #         lensPosition=camera_config["lensPosition"],
    #         h_a=movie["h_a"],
    #         bbox=bbox,
    #         resolution=0.01,
    #         **camera_config["gcps"],
    #     )
    #     raster = reshape_as_raster(corr_img)
    #     # write to temporary file
    #     OpenRiverCam.io.to_geotiff(
    #         "temp.tif",
    #         raster,
    #         transform,
    #         crs=camera_config["site"]["crs"],
    #         compress="deflate",
    #     )
    #     # Put file in bucket
    #     s3.Bucket(bucket).upload_file("temp.tif", dest_fn)
    #     n += 1
    # # clean up of temp file
    # os.remove(fn)
    # logger.info(f"{fn} sucessfully reprojected into frames in {bucket}")
    # TODO: Post status code on specific end point (Rick)
    # requests.post("http://.....", msg)
    return 200

