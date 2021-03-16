from flask_admin.contrib.sqla.filters import BaseSQLAFilter
from flask_admin import expose
from models.movie import Movie
from models.site import Site
from models.camera import CameraConfig, Camera
from views.general import UserModelView
from views.elements.s3uploadfield import s3UploadField


class FilterMovieBySite(BaseSQLAFilter):
    # Override to create an appropriate query and apply a filter to said query with the passed value from the filter UI
    def apply(self, query, value, alias=None):
        return (
            query.join(Movie.config)
            .join(CameraConfig.camera)
            .join(Camera.site)
            .filter(Site.id == value)
        )

    # readable operation name. This appears in the middle filter line drop-down
    def operation(self):
        return u"equals"

    # Override to provide the options for the filter - in this case it's a list of the titles of the Client model
    def get_options(self, view):
        return [(site.id, site.name) for site in Site.query.order_by(Site.name)]


class MovieView(UserModelView):
    column_list = (
        "config.camera.site",
        Movie.file_name,
        Movie.timestamp,
        Movie.actual_water_level,
        Movie.discharge_q50,
        Movie.status,
    )
    column_labels = {"config.camera.site": "Site"}
    column_filters = [FilterMovieBySite(column=None, name="Site")]
    column_formatters = dict(
        discharge_q05=lambda v, c, m, p: "{:.3f}".format(m.discharge_q05)
        if m.discharge_q05
        else "",
        discharge_q25=lambda v, c, m, p: "{:.3f}".format(m.discharge_q25)
        if m.discharge_q25
        else "",
        discharge_q50=lambda v, c, m, p: "{:.3f}".format(m.discharge_q50)
        if m.discharge_q50
        else "",
        discharge_q75=lambda v, c, m, p: "{:.3f}".format(m.discharge_q75)
        if m.discharge_q75
        else "",
        discharge_q95=lambda v, c, m, p: "{:.3f}".format(m.discharge_q95)
        if m.discharge_q95
        else "",
    )

    form_columns = ("config", Movie.timestamp, "file_name", Movie.actual_water_level)
    form_extra_fields = {
        "file_name": s3UploadField(
            "File", allowed_extensions=("mkv", "mpeg", "mp4")
        )
    }

    form_create_rules = ("config", "timestamp", "file_name")

    edit_template = "movie/edit.html"
    form_edit_rules = ("timestamp", "actual_water_level")

    details_template = "movie/details.html"
    column_details_list = (
        "config",
        "timestamp",
        "file_name",
        "status",
        "actual_water_level",
        "discharge_q50",
    )

    # Need this so the filter options are always up-to-date.
    @expose("/")
    def index_view(self):
        self._refresh_filters_cache()
        return super(MovieView, self).index_view()
