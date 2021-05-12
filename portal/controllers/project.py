from flask import Blueprint, jsonify
import utils

project_api = Blueprint("project_api", __name__)

@project_api.route("/api/get_epsg_codes", methods=["GET"])
def get_epsg_codes():
    """
    API endpoint to get all possible epsg codes

    :param id: bathymetry identifier
    :return:
    """
    projs = utils.get_projs()
    print(projs)
    return jsonify(projs)
