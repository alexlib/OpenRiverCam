from models.bathymetry import Bathymetry, BathymetryCoordinate
from views.general import UserModelView


class BathymetryView(UserModelView):
    column_list = (
        "site",
        Bathymetry.timestamp
    )
    form_columns = ("site", Bathymetry.timestamp, Bathymetry.crs)
    create_template = "bathymetry/create.html"
    edit_template = "bathymetry/edit.html"
