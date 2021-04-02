from flask import flash, redirect, request
from flask_admin.contrib.sqla.filters import BaseSQLAFilter
from flask_admin import expose
from flask_admin.model.helpers import get_mdict_item_or_list
from flask_admin.form import rules
from models.site import Site
from models.movie import Movie, MovieStatus
from models.camera import CameraConfig, CameraType, Camera
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

class CameraTypeView(UserModelView):
    column_list = (
        CameraType.id,
        CameraType.name,
        CameraType.lens_k1,
        CameraType.lens_c,
        CameraType.lens_f,
    )
    column_labels = {
        "id": "Camera type ID",
        "name": "Camera name",
        "lens_k1": "k1 Barrel distortion [-]",
        "lens_c": "c Optical center [-]",
        "lens_f": "f Focal length [mm]",
    }
    column_descriptions = {
        "id": "Numbered identifier of the camera type",
        "name": "Name of your camera type",
        "lens_k1": "describes the lens curvature",
        "lens_c": "describes optical center of lens (middle: 2)",
        "lens_f": "Focal length of lens, e.g. 2.8mm or 4mm",
    }



class CameraConfigView(UserModelView):
    column_list = (
        "camera",
        CameraConfig.time_start,
        CameraConfig.time_end,
        CameraConfig.movie_setting_resolution,
        CameraConfig.movie_setting_fps,
    )
    column_filters = [FilterCameraConfigBySite(column=None, name="Site")]
    form_create_rules = ("camera",)

    form_extra_fields = {
        "file_name": s3UploadFieldCameraConfig(
            "File", allowed_extensions=("mkv", "mpeg", "mp4")
        )
    }

    def validate_form(self, form):
        # flash("Custom form validation", "error")
        # return False
        return super(CameraConfigView, self).validate_form(form)

    @expose('/edit/', methods=('GET', 'POST'))
    def edit_view(self):
        id = get_mdict_item_or_list(request.args, 'id')
        model = self.get_one(id)
        movie = Movie.query.filter(Movie.config_id == model.id).order_by(Movie.id.desc()).first()
        if movie:
            self._template_args['movie'] = movie

            if movie.status == MovieStatus.MOVIE_STATUS_NEW or (model.projection_pixel_size and not model.aoi_bbox):
                self.edit_template = 'cameraconfig/edit_waiting.html'
            elif model.aoi_bbox:
                self.form_edit_rules = (
                    "aoi_window_size",
                )
                self.edit_template = 'cameraconfig/edit_step3.html'
            else:
                self.form_edit_rules = (
                    "gcps_src_0_x",
                    "gcps_src_0_y",
                    "gcps_src_1_x",
                    "gcps_src_1_y",
                    "gcps_src_2_x",
                    "gcps_src_2_y",
                    "gcps_src_3_x",
                    "gcps_src_3_y",
                    "gcps_dst_0_x",
                    "gcps_dst_0_y",
                    "gcps_dst_1_x",
                    "gcps_dst_1_y",
                    "gcps_dst_2_x",
                    "gcps_dst_2_y",
                    "gcps_dst_3_x",
                    "gcps_dst_3_y",
                    "gcps_z_0",
                    "gcps_h_ref",
                    "corner_up_left_x",
                    "corner_up_left_y",
                    "corner_up_right_x",
                    "corner_up_right_y",
                    "corner_down_left_x",
                    "corner_down_left_y",
                    "corner_down_right_x",
                    "corner_down_right_y",
                    "lens_position_x",
                    "lens_position_y",
                    "lens_position_z",
                    "projection_pixel_size"
                )
                self.edit_template = 'cameraconfig/edit_step2.html'
        else:
            self.form_edit_rules = (
                "time_start",
                "time_end",
                "file_name",
            )
            self.edit_template = 'cameraconfig/edit_step1.html'

        self._form_edit_rules = rules.RuleSet(self, self.form_edit_rules)
        return super(CameraConfigView, self).edit_view()

    # Need this so the filter options are always up-to-date.
    @expose("/")
    def index_view(self):
        self._refresh_filters_cache()
        return super(CameraConfigView, self).index_view()
