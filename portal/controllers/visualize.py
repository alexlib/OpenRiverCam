import io
import xarray as xr
import numpy as np
import utils
import re

from flask import Blueprint, jsonify, request, make_response
from models.movie import Movie, MovieStatus

visualize_api = Blueprint("visualize_api", __name__)

@visualize_api.route("/api/visualize/get_snapshot/<id>", methods=["GET"])
def get_snapshot(id):
    movie = Movie.query.get(id)
    if not movie:
        raise ValueError("Invalid movie with identifier %s" % id)

    if not movie.file_bucket:
        raise ValueError("Movie does not have a S3 bucket assigned")

    s3 = utils.get_s3()
    bucket_name = movie.file_bucket
    bucket_name = 'example' # TODO: Remove overwrite!

    # Get all snapshots from bucket.
    regex = re.compile('frame.*\.jpg')
    file_objects = [ f for f in list(map(lambda f: f.key, s3.Bucket(bucket_name).objects.all())) if regex.match(f) ]
    if not len(file_objects):
        raise ValueError("Could not locate snapshot")

    # Get first extracted frame of the movie.
    file = s3.Object(bucket_name, sorted(file_objects)[0]).get()

    # Return file with content headers.
    response = make_response(file['Body'].read())
    response.headers['Content-Type'] = 'image/jpeg'
    return response

@visualize_api.route("/api/visualize/get_projected_snapshot/<id>", methods=["GET"])
def get_projected_snapshot(id):
    movie = Movie.query.get(id)
    if not movie:
        raise ValueError("Invalid movie with identifier %s" % id)

    if not movie.file_bucket:
        raise ValueError("Movie does not have a S3 bucket assigned")

    s3 = utils.get_s3()
    bucket_name = movie.file_bucket
    bucket_name = 'example' # TODO: Remove overwrite!

    # Get all snapshots from bucket.
    regex = re.compile('proj.*\.png')
    file_objects = [ f for f in list(map(lambda f: f.key, s3.Bucket(bucket_name).objects.all())) if regex.match(f) ]
    if not len(file_objects):
        raise ValueError("Could not locate snapshot")

    # Get first extracted frame of the movie.
    file = s3.Object(bucket_name, sorted(file_objects)[0]).get()

    # Return file with content headers.
    response = make_response(file['Body'].read())
    response.headers['Content-Type'] = 'image/png'
    return response

def xyla(u, v, res=0.01):
    """
    compute x, y, length and angle of vectors to plot with Highcharts.
    0 deg. is south
    90 deg. is east
    180 deg. north
    270 deg. west

    :param u:
    :param v:
    :return:
    """
    length = (u.values**2 + v.values**2)**0.5
    angle = np.arctan2(-u.values, -v.values) * 180 / np.pi
    xi, yi = np.meshgrid(u.x.values/res, u.y.values/res)
    # remove missings
    idx = np.isfinite(length)
    xi, yi, length, angle = xi[idx], yi[idx], length[idx], angle[idx]
    data = [[round(_xi), round(_yi), _length, _angle] for _xi, _yi, _length, _angle in zip(xi, yi, length, angle)]
    xmin = int(round((u.x.values[0] - np.diff(u.x.values).min() / 2)/res))
    xmax = int(round((u.x.values[-1] + np.diff(u.x.values).min() / 2)/res))
    ymin = int(round((u.y.values[-1] + np.diff(u.y.values).min() / 2)/res))
    ymax = int(round((u.y.values[0] - np.diff(u.y.values).min() / 2)/res))

    return {
        "xmin": xmin,
        "xmax": xmax,
        "ymin": ymin,
        "ymax": ymax,
        "data": data,
    }

@visualize_api.route("/api/visualize/get_velocity_vectors/<id>", methods=["GET"])
def get_velocity_vectors(id):
    movie = Movie.query.get(id)
    if not movie:
        raise ValueError("Invalid movie with identifier %s" % id)

    s3 = utils.get_s3()
    bucket_name = movie.file_bucket
    bucket_name = 'example' # TODO: Remove overwrite!

    file_stream = io.BytesIO()
    s3.Object(bucket_name, 'velocity_filter.nc').download_fileobj(file_stream)
    file_stream.seek(0)

    ds = xr.open_dataset(file_stream, engine='h5netcdf')
    # extract vectors and convert to Highchart data array
    u = ds["v_x"].median(dim="time")
    v = ds["v_y"].median(dim="time")
    data = xyla(u, v)

    return jsonify(data)


@visualize_api.errorhandler(ValueError)
def handle(e):
    return (
        jsonify({"error": "Invalid request", "message": str(e)}),
        400,
    )