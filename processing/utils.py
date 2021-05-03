import boto3
import os
import ibm_boto3
from ibm_botocore.client import Config

def get_s3():
    return boto3.resource(
        "s3",
        endpoint_url=os.getenv("S3_ENDPOINT_URL"),
        aws_access_key_id=os.getenv("S3_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("S3_ACCESS_SECRET"),
        config=boto3.session.Config(signature_version="s3v4"),
    ) if os.getenv("FLASK_ENV") != "ibmcloud" else ibm_boto3.resource('s3',
        ibm_api_key_id=os.getenv('S3_ACCESS_KEY'),
        ibm_service_instance_id=os.getenv('S3_ACCESS_SECRET'),
        ibm_auth_endpoint=os.getenv('COS_AUTH_ENDPOINT'),
        config=Config(signature_version="oauth"),
        endpoint_url=os.getenv('S3_ENDPOINT_URL')
    )