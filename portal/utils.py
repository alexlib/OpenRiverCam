import boto3
import os
import pyproj
import ibm_boto3
from ibm_botocore.client import Config

def get_s3():
    """
    Get boto3 resource connection to the S3 file storage.

    :return:
    """
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

def get_projs(user_projs=[]):
    """
    Retrieve a serializable list of pyproj supported codes. Currently supported are all UTM zones and Latitude-longitude
    user_projs are additional projections requested by user in epsg code integer format
    """
    latlong = [4326]
    utm = list(range(32601, 32661)) + list(range(32701, 32761))
    others = [28992, ]  # dutch Rijksdriehoek
    all_codes = user_projs + latlong + utm + others
    crs_list = [{"epsg": code, "name": pyproj.CRS.from_epsg(code).name if code != 4326 else " WGS84 Latitude Longitude"} for code in all_codes]
    return crs_list