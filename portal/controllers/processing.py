from flask import Blueprint, jsonify, request
from models.movie import Movie, MovieStatus
from models.camera import CameraConfig
from models import db
from jsonschema import validate, ValidationError
import json

processing_api = Blueprint("processing_api", __name__)


@processing_api.route("/api/processing/extract_frames/<id>", methods=["POST"])
def processing_extract_frames(id):
    """
    API endpoint for processing callback to set movie status to extracted.

    :param id: movie identifier
    :rtype: object
    """
    movie = Movie.query.get(id)
    if not movie:
        raise ValueError("Invalid movie with identifier %s" % id)

    movie.status = MovieStatus.MOVIE_STATUS_EXTRACTED

    db.commit()
    return jsonify(movie.to_dict())


@processing_api.route("/api/processing/run/<id>", methods=["POST"])
def processing_compute_piv(id):
    """
    API endpoint for processing callback to set movie status to finished and store discharge results.

    :param id: movie identifier
    :rtype: object
    """
    schema = {
        "type": "object",
        "properties": {
            "discharge_q05": {"type": "number"},
            "discharge_q25": {"type": "number"},
            "discharge_q50": {"type": "number"},
            "discharge_q75": {"type": "number"},
            "discharge_q95": {"type": "number"},
        },
        "minProperties": 5,
        "additionalProperties": False,
    }

    content = request.get_json(silent=True)
    validate(instance=content, schema=schema)
    movie = Movie.query.get(id)
    if not movie:
        raise ValueError("Invalid movie with identifier %s" % id)

    for key, value in content.items():
        setattr(movie, key, value)
    movie.status = MovieStatus.MOVIE_STATUS_FINISHED

    db.commit()
    return jsonify(movie.to_dict())

@processing_api.route("/api/processing/get_aoi/<id>", methods=["POST"])
def processing_get_aoi(id):
    """
    API endpoint for processing callback to set camera configuration AOI Bbox.

    :param id: camera config identifier
    :rtype: object
    """
    schema = {
        "type": "object",
        "properties": {
            "crs": {"type": "object"},
            "features": {"type": "array"},
            "type": {"type": "string"},
        },
        "minProperties": 3,
        "additionalProperties": False,
    }

    content = request.get_json(silent=True)
    print(content)
    validate(instance=content, schema=schema)
    camera_config = CameraConfig.query.get(id)
    if not camera_config:
        raise ValueError("Invalid camera config with identifier %s" % id)

    camera_config.aoi_bbox = json.dumps(content)

    db.commit()
    return jsonify(camera_config.to_dict())

@processing_api.route("/api/processing/error/<id>", methods=["POST"])
def processing_error(id):
    """
    API endpoint for processing callback to set error status and message on movie.

    :param id: movie identifier
    :rtype: object
    """
    schema = {
        "type": "object",
        "properties": {"error_message": {"type": "string"}},
        "minProperties": 1,
        "additionalProperties": False,
    }

    movie = Movie.query.get(id)
    if not movie:
        raise ValueError("Invalid movie with identifier %s" % id)

    content = request.get_json(silent=True)
    validate(instance=content, schema=schema)
    for key, value in content.items():
        setattr(movie, key, value)
    movie.status = MovieStatus.MOVIE_STATUS_ERROR
    db.commit()
    return jsonify(movie.to_dict())


@processing_api.errorhandler(ValidationError)
@processing_api.errorhandler(ValueError)
def handle(e):
    """
    Custom error handling for processing API endpoints.

    :param e:
    :return:
    """
    return (
        jsonify({"error": "Invalid input for processing callback", "message": str(e)}),
        400,
    )
