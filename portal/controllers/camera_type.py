from flask import Blueprint, jsonify, request
from models.camera import CameraType
from models import db, Base

camera_type_api = Blueprint('camera_type_api', __name__)

@camera_type_api.route("/api/camera_type", methods=['GET'])
def camera_type_list():
    camera_types = CameraType.query.all()
    return jsonify([ct.to_dict() for ct in camera_types])

@camera_type_api.route("/api/camera_type/<id>", methods=['GET'])
def camera_type_get(id):
    camera_type = CameraType.query.get(id)
    return jsonify(camera_type.to_dict())

@camera_type_api.route("/api/camera_type", methods=['POST'])
def camera_type_post():
    content = request.get_json(silent=True)
    camera_type = CameraType(
        name = content['name']
    )
    db.add(camera_type)
    db.commit()
    db.refresh(camera_type)
    return jsonify(camera_type.to_dict())

@camera_type_api.route("/api/camera_type/<id>", methods=['PUT'])
def camera_type_put(id):
    return jsonify({"name": "Camera %s" % id})

@camera_type_api.route("/api/camera_type/<id>", methods=['DELETE'])
def camera_type_delete(id):
    return jsonify({"name": "Camera %s" % id})