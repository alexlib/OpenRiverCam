from flask_admin.contrib.sqla.filters import BaseSQLAFilter
from flask_admin import expose
from models.site import Site
from models.camera import CameraConfig, Camera
from views.general import UserModelView

class FilterCameraConfigBySite(BaseSQLAFilter):
    # Override to create an appropriate query and apply a filter to said query with the passed value from the filter UI
    def apply(self, query, value, alias=None):
        return query.join(CameraConfig.camera).join(Camera.site).filter(Site.id == value)

    # readable operation name. This appears in the middle filter line drop-down
    def operation(self):
        return u'equals'

    # Override to provide the options for the filter - in this case it's a list of the titles of the Client model
    def get_options(self, view):
        return [(site.id, site.name) for site in Site.query.order_by(Site.name)]

class CameraConfigView(UserModelView):
    column_list = ("camera", CameraConfig.time_start, CameraConfig.time_end, CameraConfig.movie_setting_resolution, CameraConfig.movie_setting_fps)
    column_filters = [FilterCameraConfigBySite(column=None, name='Site')]

    # Need this so the filter options are always up-to-date.
    @expose('/')
    def index_view(self):
        self._refresh_filters_cache()
        return super(CameraConfigView, self).index_view()