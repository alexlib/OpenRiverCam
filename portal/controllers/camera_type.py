from flask import Blueprint, jsonify, request
from models.camera import CameraType
from models import db
from jsonschema import validate, ValidationError

camera_type_api = Blueprint('camera_type_api', __name__)
schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "lens_c": {"type": "number"},
        "lens_f": {"type": "number"},
        "lens_k1": {"type": "number"}
    },
    "minProperties": 4,
    "additionalProperties": False
}

@camera_type_api.route("/api/camera_type", methods=['GET'])
def camera_type_list():
    camera_types = CameraType.query.order_by(CameraType.id.asc()).all()
    return jsonify([ct.to_dict() for ct in camera_types])

@camera_type_api.route("/api/camera_type/<id>", methods=['GET'])
def camera_type_get(id):
    camera_type = CameraType.query.get(id)
    if not camera_type:
        raise ValueError('Invalid camera type with identifier %s' % id)
    return jsonify(camera_type.to_dict())

@camera_type_api.route("/api/camera_type", methods=['POST'])
def camera_type_post():
    content = request.get_json(silent=True)
    validate(instance=content, schema=schema)
    camera_type = CameraType(**content)
    db.add(camera_type)
    db.commit()
    db.refresh(camera_type)
    return jsonify(camera_type.to_dict())

@camera_type_api.route("/api/camera_type/<id>", methods=['PUT'])
def camera_type_put(id):
    content = request.get_json(silent=True)
    validate(instance=content, schema=schema)
    camera_type = CameraType.query.get(id)
    if not camera_type:
        raise ValueError('Invalid camera type with identifier %s' % id)

    for key, value in content.items():
        setattr(camera_type, key, value)

    db.commit()
    return jsonify(camera_type.to_dict())

@camera_type_api.route("/api/camera_type/<id>", methods=['DELETE'])
def camera_type_delete(id):
    camera_type = CameraType.query.get(id)
    if not camera_type:
        raise ValueError('Invalid camera type with identifier %s' % id)

    db.delete(camera_type)
    db.commit()
    return jsonify(camera_type.to_dict())

@camera_type_api.errorhandler(ValidationError)
@camera_type_api.errorhandler(ValueError)
def handle(e):
    return jsonify({"error": "Invalid input for camera type", "message": str(e)}), 400