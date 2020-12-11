import os
import boto3
import OpenRiverCam
import logging
import io

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
    # TODO: finalize implementation
    # Example upload file to S3.
    s3 = boto3.resource('s3',
                        endpoint_url=os.getenv('MINIO_ACCESS_URL'),
                        aws_access_key_id=os.getenv('S3_ACCESS_KEY'),
                        aws_secret_access_key=os.getenv('S3_ACCESS_SECRET'),
                        config=boto3.session.Config(signature_version='s3v4')
                        )

    # Create bucket if it doesn't exist yet.
    if s3.Bucket(bucket) not in s3.buckets.all():
        s3.create_bucket(Bucket=bucket)
    with open(fn, "rb") as f:
        buf = io.BytesIO(f.read())
    # Seek beginning of in-memory file before storing.
    buf.seek(0)
    s3.Object(bucket, dest).put(Body=buf)
    print("Uploading is done!")



def extract_frames(movie, camera, dest, prefix="frame_", logger=logging):
    # open S3 bucket
    s3 = boto3.resource('s3',
                        endpoint_url='http://storage:9000',
                        aws_access_key_id=os.getenv('S3_ACCESS_KEY'),
                        aws_secret_access_key=os.getenv('S3_ACCESS_SECRET'),
                        config=boto3.session.Config(signature_version='s3v4')
                        )

    # Create bucket if it doesn't exist yet.
    if s3.Bucket('test-bucket') not in s3.buckets.all():
        s3.create_bucket(Bucket='test-bucket')


    n = 0
    fns = []
    t = []
    logger.info(f"Writing movie {movie['file']['identifier']} to {dest}")
    # open file from bucket in memory
    mov = io.BytesIO()
    s3.Object(movie["file"]["bucket"], movie["file"]["identifier"]).download_fileobj(mov)
    with open(movie["file"]["identifier"], 'wb') as f:
        f.write(mov)
    for _t, buf in OpenRiverCam.io.frames(movie["file"]["identifier"], lens_pars=camera["lensParameters"]):
        # Bucket filename
        dest_fn = os.path.join(dest, '{:s}{:04d}.jpg'.format(prefix, n))
        logger.debug(f"Write frame {n} in {dest_fn} to S3")
        # Seek beginning of bytestream
        buf.seek(0)
        # Put file in bucket
        s3.Object(movie["file"]["bucket"], dest_fn).put(Body=buf)
        n += 1
        # add file and timestamp to list
        t += _t
        fns += dest_fn

    # TODO: Post status code on specific end point
    # requests.post("http://.....", msg)
    # r = 200  # Rick, agree on format for response body. I assume an error code (success: 200), and a data body
    return 200
#     "type": "extract_snapshots",
#     "kwargs": {
#         "movie": {
#             "file": {
#                 "bucket": "test-bucket",
#                 "identifier": "schedule_20201120_142304.mkv"
#             }
#         },
#         "camera": {
#             "name": "Foscam E9900P",
#             "configuration": {},
#             "lensParameters": {
#                 "k": 0.5
#             }
#         }
#     }
#
# }
#
#     lens_pars = {
#         "k1": -10.0e-6,
#         "c": 2,
#         "f": 8.0,
#     }
