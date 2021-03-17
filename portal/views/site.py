from flask_admin import expose
from models.movie import Movie
from models.site import Site
from models.camera import CameraConfig, Camera
from views.general import UserModelView


class SiteView(UserModelView):
    column_list = (
        Site.id,
        Site.name,
        Site.position_x,
        Site.position_y,
        Site.position_crs,
    )

    print(f"Check site name {str(Site.name)}")
    column_labels = {
        "id": "Site ID",
        "name": "Site name",
        "position_x": "Longitude [deg]",
        "position_y": "Latitude [deg]",
        "position_crs": "EPSG code",
    }

    column_descriptions = {
        "id": "Numbered identifier of the site",
        "name": "Name of your site",
        "position_x": "Longitude in Decimal Degrees",
        "position_y": "Latitude in Decimal Degrees",
        "position_crs": "Local coordinate reference system as EPSG code",
    }

    column_formatters = dict(
        position_x=lambda v, c, m, p: "{:.8f}".format(m.position_x)
        if m.position_x
        else "",
        position_y=lambda v, c, m, p: "{:.8f}".format(m.position_y)
        if m.position_y
        else "",
        position_crs=lambda v, c, m, p: "EPSG:{:d}".format(m.position_crs)
        if m.position_crs
        else "",
    )

    list_template = "site/list.html"
    create_template = "site/create.html"
    edit_template = "site/edit.html"
    details_template = "site/details.html"