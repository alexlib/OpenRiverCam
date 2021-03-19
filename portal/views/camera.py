from flask_admin.contrib.sqla.filters import BaseSQLAFilter
from flask_admin import expose
from models.site import Site
from models.camera import CameraConfig, Camera
from views.general import UserModelView
from views.elements.s3uploadfield import s3UploadFieldCameraConfig


class FilterCameraConfigBySite(BaseSQLAFilter):
    # Override to create an appropriate query and apply a filter to said query with the passed value from the filter UI
    def apply(self, query, value, alias=None):
        return (
            query.join(CameraConfig.camera).join(Camera.site).filter(Site.id == value)
        )

    # readable operation name. This appears in the middle filter line drop-down
    def operation(self):
        return u"equals"

    # Override to provide the options for the filter - in this case it's a list of the titles of the Client model
    def get_options(self, view):
        return [(site.id, site.name) for site in Site.query.order_by(Site.name)]


class CameraConfigView(UserModelView):
    column_list = (
        "camera",
        CameraConfig.time_start,
        CameraConfig.time_end,
        CameraConfig.movie_setting_resolution,
        CameraConfig.movie_setting_fps,
    )
    column_filters = [FilterCameraConfigBySite(column=None, name="Site")]

    form_columns = ("camera", CameraConfig.time_start, CameraConfig.time_end, "file_name")
    form_create_rules = ("camera",)
    form_edit_rules = ("time_start", "time_end", "file_name")

    form_extra_fields = {
        "file_name": s3UploadFieldCameraConfig(
            "File", allowed_extensions=("mkv", "mpeg", "mp4")
        )
    }

    # Need this so the filter options are always up-to-date.
    @expose("/")
    def index_view(self):
        self._refresh_filters_cache()
        return super(CameraConfigView, self).index_view()
