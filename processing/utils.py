import boto3
import os

def get_s3():
    return boto3.resource(
        "s3",
        endpoint_url=os.getenv("MINIO_ACCESS_URL"),
        aws_access_key_id=os.getenv("S3_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("S3_ACCESS_SECRET"),
        config=boto3.session.Config(signature_version="s3v4"),
    )

# def list_files_s3(s3, bucket, wildcard):
