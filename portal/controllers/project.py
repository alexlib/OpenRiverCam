from flask import Blueprint, jsonify, request, flash, url_for, redirect
from models.site import Site
from models import db
from jsonschema import validate, ValidationError
from io import StringIO
import csv
import utils

project_api = Blueprint("project_api", __name__)


@project_api.route("/api/get_epsg_codes/<id>", methods=["GET"])
def get_epsg_codes(id):
    """
    API endpoint to get all possible epsg codes

    :param id: bathymetry identifier
    :return:
    """
    site = Site.query.get(id)
    print(site)
    if not site:
        raise ValueError("Invalid site with identifier %s" % id)
    epsg_site = site.position_crs
    projs = utils.get_projs([epsg_site])
    print(projs)
    return jsonify(projs)
