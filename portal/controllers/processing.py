from flask import Blueprint, jsonify, request
from models.movie import Movie, MovieStatus
from models import db
from jsonschema import validate, ValidationError

processing_api = Blueprint("processing_api", __name__)


@processing_api.route("/api/processing/extract_frames/<id>", methods=["POST"])
def processing_extract_frames(id):
    movie = Movie.query.get(id)
    if not movie:
        raise ValueError("Invalid movie with identifier %s" % id)

    movie.status = MovieStatus.MOVIE_STATUS_EXTRACTED

    db.commit()
    return jsonify(movie.to_dict())


@processing_api.route("/api/processing/run/<id>", methods=["POST"])
def processing_compute_piv(id):
    # schema = {
    #     "type": "object",
    #     "properties": {
    #         "discharge": {"type": "number"}
    #     },
    #     "minProperties": 1,
    #     "additionalProperties": False
    # }
    #
    # content = request.get_json(silent=True)
    # validate(instance=content, schema=schema)
    movie = Movie.query.get(id)
    if not movie:
        raise ValueError("Invalid movie with identifier %s" % id)

    # for key, value in content.items():
    #     setattr(movie, key, value)
    movie.status = MovieStatus.MOVIE_STATUS_FINISHED

    db.commit()
    return jsonify(movie.to_dict())


@processing_api.route("/api/processing/error/<id>", methods=["POST"])
def processing_error(id):
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
    return (
        jsonify({"error": "Invalid input for processing callback", "message": str(e)}),
        400,
    )
