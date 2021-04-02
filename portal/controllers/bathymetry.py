from flask import Blueprint, jsonify, request
from models.bathymetry import Bathymetry, BathymetryCoordinate
from models import db
from jsonschema import validate, ValidationError

bathymetry_api = Blueprint("bathymetry_api", __name__)
schema = {
    "type": "object",
    "properties": {
        "coordinates": {
            "type": "array",
            "items": {
                "x": {"type": "number"},
                "y": {"type": "number"},
                "z": {"type": "number"}
            }
        }
    }
}

@bathymetry_api.route("/api/bathymetry/<id>", methods=["POST"])
def bathymetry_coordinates(id):
    content = request.get_json(silent=True)
    validate(instance=content, schema=schema)
    bathymetry = Bathymetry.query.get(id)
    if not bathymetry:
        raise ValueError("Invalid bathymetry with identifier %s" % id)

    BathymetryCoordinate.query.filter(BathymetryCoordinate.bathymetry_id == bathymetry.id).delete()
    for coordinate in content["coordinates"]:
        db.add(BathymetryCoordinate(x=coordinate['x'],y=coordinate['y'],z=coordinate['z'],bathymetry_id=bathymetry.id));

    db.commit()
    return jsonify(bathymetry.to_dict())

@bathymetry_api.errorhandler(ValidationError)
@bathymetry_api.errorhandler(ValueError)
def handle(e):
    return jsonify({"error": "Invalid input for bathymetry", "message": str(e)}), 400
