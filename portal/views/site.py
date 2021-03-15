from flask_admin import expose
from models.movie import Movie
from models.site import Site
from models.camera import CameraConfig, Camera
from views.general import UserModelView

class SiteView(UserModelView):
    # DO STUFF
    column_list = (
        Site.name,
        Site.position_crs,
        Site.position_x,
        Site.position_y,
    )
    print(f"Check site name {str(Site.name)}")
    column_labels = {"name": "Site name",
                     "position_crs": "EPSG code",
                     "position_x": "Longitude [deg]",
                     "position_y": "Latitude [deg]",
                     }

    column_descriptions = {"name": "Name of your site",
                     "position_crs": "Local coordinate reference system as EPSG code",
                     "position_x": "Longitude in Decimal Degrees",
                     "position_y": "Latitude in Decimal Degrees",
                     }

    column_formatters = dict(
        position_crs=lambda v, c, m, p: "EPSG:{:d}".format(m.position_crs)
        if m.position_crs
        else "",
        position_x=lambda v, c, m, p: "{:.8f}".format(m.position_x)
        if m.position_x
        else "",
        position_y=lambda v, c, m, p: "{:.8f}".format(m.position_y)
        if m.position_y
        else "",
    )

    list_template = "site/list.html"
