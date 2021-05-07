from flask import Blueprint, jsonify, request
from models.ratingcurve import RatingCurve, RatingPoint
from models import db
from jsonschema import validate, ValidationError

ratingcurve_api = Blueprint("ratingcurve_api", __name__)
schema = {
    "type": "object",
    "properties": {
        "ratingpoints": {
            "type": "array",
            "items": {
                "movie_id": {"type": "number"},
                "include": {"type": "boolean"}
            }
        }
    }
}

@ratingcurve_api.route("/api/ratingpoints/<id>", methods=["POST"])
def ratingpoints_included(id):
    """
    API endpoint to update which rating points should be included in a specific rating curve.

    :param id: ratingcurve identifier
    :rtype: object
    """
    content = request.get_json(silent=True)
    validate(instance=content, schema=schema)
    ratingcurve = RatingCurve.query.get(id)
    if not ratingcurve:
        raise ValueError("Invalid ratingpoint with identifier %s" % id)

    for rp in content['ratingpoints']:
        ratingPoint = RatingPoint.query.filter(RatingPoint.movie_id == rp['movie_id'], RatingPoint.ratingcurve_id == ratingcurve.id).first()
        ratingPoint.include = True if rp['include'] else False

    db.commit()
    return jsonify(ratingcurve.to_dict())

@ratingcurve_api.errorhandler(ValidationError)
@ratingcurve_api.errorhandler(ValueError)
def handle(e):
    """
    Custom error handling for ratingcurve API endpoints.

    :param e:
    :return:
    """
    return jsonify({"error": "Invalid input for rating curve points", "message": str(e)}), 400
