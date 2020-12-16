import os
import OpenRiverCam
import utils
import logging

def upload_file(fn, bucket, dest=None):
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
    print("Uploading is done!")



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
    logger.info(f"Writing movie {movie['file']['identifier']} to {movie['file']['bucket']}")
    # open file from bucket in memory
    bucket = movie["file"]["bucket"]
    fn = movie["file"]["identifier"]
    # make a temporary file
    s3.Bucket(bucket).download_file(fn, fn)
    for _t, buf in OpenRiverCam.io.frames(
        fn, lens_pars=camera["lensParameters"]
    ):
        # filename in bucket, following template frame_{4-digit_framenumber}_{time_in_milliseconds}.jpg
        dest_fn = "{:s}_{:04d}_{:06d}.jpg".format(prefix, n, int(_t*1000))
        logger.debug(f"Write frame {n} in {dest_fn} to S3")
        # Seek beginning of bytestream
        buf.seek(0)
        print(len(buf.getvalue()))
        # Put file in bucket
        s3.Object(bucket, dest_fn).put(Body=buf)
        n += 1
    # clean up of temp file
    os.remove(fn)
    # TODO: Post status code on specific end point (Rick)
    # requests.post("http://.....", msg)
    return 200

def extract_project_frames(movie, camera_config, prefix="proj", logger=logging):
    """
    Extract frames, lens correct, greyscale correct and project to defined AOI with GCPs, water level and camera position
    Results in GeoTIFF files in desired projection and resolution within bucket defined in movie
    :param movie: dict, movie information
    :param camera_config: dict, camera_config containing camera properties, aoi, gcps, site, camera position
    :param prefix="proj": str, prefix of file names, used in storage bucket
    :param logger=logging: logging obj
    :return:
    """
    # FIXME: implement
    # TODO check on time frame of movie and validity of the camera_config
    # TODO check if aoi is defined, without it, projection is not possible
    # TODO check if gcps are defined, without it projection not possible
    # TODO check resolution, without set resolution, not possible to reproject
    # TODO reprojection implementation based on AOI object and resolution
    # TODO storage in BytesIO representation of GeoTIFF (rasterio) and push to bucket
    raise NotImplementedError("Implement me")
    # post request
    return 200

def get_aoi(camera_config):
    gcps
    src_corners
    crs
    # call OpenRiverCam.ortho.get_aoi()


def compute_v():
    """
    compute velocities over frame pairs, choosing frame interval, start / end frame.

    :return:
    """
