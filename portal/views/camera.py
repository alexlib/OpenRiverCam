from flask import flash, redirect, request
from flask_admin.contrib.sqla.filters import BaseSQLAFilter
from flask_admin import expose
from flask_admin.model.helpers import get_mdict_item_or_list
from flask_admin.form import rules
from flask_admin.helpers import is_form_submitted, validate_form_on_submit
from flask_security import current_user
from sqlalchemy.exc import IntegrityError
from models.site import Site
from models.movie import Movie, MovieStatus, MovieType
from models.camera import CameraConfig, CameraType, Camera
from views.general import UserModelView
from views.elements.s3uploadfield import s3UploadFieldCameraConfig
from sqlalchemy import inspect
from math import sqrt


class FilterCameraConfigBySite(BaseSQLAFilter):
    def apply(self, query, value, alias=None):
        """
        Override to create an appropriate query and apply a filter to said query with the passed value from the filter UI

        :param query:
        :param value:
        :param alias:
        :return:
        """
        return (
            query
                .filter(Site.id == value)
                .filter(Site.user_id == current_user.id)
        )

    def operation(self):
        """
        Readable operation name. This appears in the middle filter line drop-down

        :return:
        """
        return u"equals"

    def get_options(self, view):
        """
        Override to provide the options for the filter - in this case it's a list of the titles of the Client model

        :param view:
        :return:
        """
        return [(site.id, site.name) for site in (Site.query.filter_by(user_id=current_user.id).order_by(Site.name) if current_user else [])]


class CameraConfigView(UserModelView):
    create_template = "cameraconfig/create.html"
    column_list = (
        "camera",
        CameraConfig.time_start,
        CameraConfig.time_end,
        CameraConfig.movie_setting_resolution,
        CameraConfig.movie_setting_fps,
    )
    column_labels = {
        "aoi_window_size": "Window size [pixels]"

    }
    column_filters = [FilterCameraConfigBySite(column=None, name="Site")]
    form_create_rules = ("camera",)
    form_extra_fields = {
        "file_name": s3UploadFieldCameraConfig(
            "File", allowed_extensions=("mkv", "mpeg", "mp4")
        )
    }
    form_args = {
        "camera": {
            "query_factory": lambda: Camera.query.join(Site).filter_by(
                user_id=current_user.id
            )
        }
    }

    def validate_form(self, form):
        """
        Additional server side validation for camera config. Calculate max distance between the GCPS coordinates.

        :param form:
        :return:
        """
        if is_form_submitted():
            prevent_submit = False
            # Get list of all model attributes.
            mapper = inspect(CameraConfig)
            for column in mapper.attrs:
                # Check if model attribute is present in this form.
                if column.key != "time_end" and column.key != "crs" and hasattr(form, column.key) and getattr(form, column.key) is not None:
                    # Check if data is set for this form field.
                    if getattr(form, column.key).data is None:
                        getattr(form, column.key).errors = ['Required']
                        prevent_submit = True

            # Check for max distance between ground control points.
            if hasattr(form, "gcps_dst_0_x") and getattr(form, "gcps_dst_0_x") is not None and not prevent_submit:
                gcps = []
                for i in range(4):
                    if hasattr(form, "gcps_dst_{}_x".format(i)) and hasattr(form, "gcps_dst_{}_y".format(i)):
                        gcps.append([float(getattr(form, "gcps_dst_{}_x".format(i)).data), float(getattr(form, "gcps_dst_{}_y".format(i)).data)])

                for i in range(len(gcps)):
                    for j in range(i + 1, len(gcps)):
                        distance = sqrt(pow(gcps[i][0] - gcps[j][0],2) + pow(gcps[i][1] - gcps[j][1],2))
                        if distance > 25:
                            flash("Distance between ground control points {} and {} is {:.1f} meters.".format(i+1, j+1, distance), "error")
                            return False

            if prevent_submit:
                return False

        return super(CameraConfigView, self).validate_form(form)

    @expose('/edit/', methods=('GET', 'POST'))
    def edit_view(self):
        """
        Over-write default edit_view with the multi-step forms.

        :return:
        """
        id = get_mdict_item_or_list(request.args, 'id')
        model = self.get_one(id)
        movie = Movie.query.filter(Movie.config_id == model.id).filter(Movie.type == MovieType.MOVIE_TYPE_CONFIG).order_by(Movie.id.desc()).first()
        if movie:
            self._template_args['movie'] = movie
            if movie.status == MovieStatus.MOVIE_STATUS_NEW or (model.gcps_src_0_x and not model.aoi_bbox):
                self.edit_template = 'cameraconfig/edit_waiting.html'
            elif model.aoi_bbox:
                self.form_edit_rules = (
                    "aoi_window_size",
                )
                self.edit_template = 'cameraconfig/edit_step3.html'
            else:
                self.form_edit_rules = (
                    "crs",
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

    @expose("/")
    def index_view(self):
        """
        Ensure the filter options are always up-to-date.

        :return:
        """
        self._refresh_filters_cache()
        return super(CameraConfigView, self).index_view()

    def get_query(self):
        """
        Don't show config for sites which are not from this user.

        :return:
        """
        return super(CameraConfigView, self).get_query().join(Camera).join(Site).filter_by(user_id=current_user.id)

    def get_one(self, id):
        """
        Don't allow to access a specific config if it's not from this user.

        :param id:
        :return:
        """
        return super(CameraConfigView, self).get_query().filter_by(id=id).join(Camera).join(Site).filter_by(user_id=current_user.id).one()

    def handle_view_exception(self, e):
        """
        Human readable error message for database integrity errors.

        :param e:
        :return:
        """
        if isinstance(e, IntegrityError):
            flash("Camera config can\'t be deleted since it\'s being used by movies. You\'ll need to delete those movies first.", "error")
            return True

        return super(ModelView, self).handle_view_exception(exc)

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

    def get_query(self):
        """
        Don't show camera types which are not from this user.

        :return:
        """
        return super(CameraTypeView, self).get_query().filter_by(user_id=current_user.id)

    def get_one(self, id):
        """
        Don't allow to access a specific camera type if it's not from this user.

        :param id:
        :return:
        """
        return super(CameraTypeView, self).get_query().filter_by(id=id).filter_by(user_id=current_user.id).one()

    def on_model_change(self, form, model, is_created):
        """
        Store the user id of the creator to link the camera type to this account.

        :param form:
        :param model:
        :param is_created:
        """
        if is_created:
            model.user_id = current_user.id

    def handle_view_exception(self, e):
        """
        Human readable error message for database integrity errors.

        :param e:
        :return:
        """
        if isinstance(e, IntegrityError):
            flash("Camera type can\'t be deleted since it\'s being used by a camera. You\'ll need to delete that camera first.", "error")
            return True

        return super(ModelView, self).handle_view_exception(exc)

class CameraView(UserModelView):
    form_args = {
        "site": {
            "query_factory": lambda: Site.query.filter_by(
                user_id=current_user.id
            )
        },
        "camera_type": {
            "query_factory": lambda: CameraType.query.filter_by(
                user_id=current_user.id
            )
        }
    }

    def get_query(self):
        """
        Don't show cameras for sites which are not from this user.

        :return:
        """
        return super(CameraView, self).get_query().join(Site).filter_by(user_id=current_user.id)

    def get_one(self, id):
        """
        Don't allow to access a specific camera if it's not from this user.

        :param id:
        :return:
        """
        return super(CameraView, self).get_query().filter_by(id=id).join(Site).filter_by(user_id=current_user.id).one()

    def handle_view_exception(self, e):
        """
        Human readable error message for database integrity errors.

        :param e:
        :return:
        """
        if isinstance(e, IntegrityError):
            flash("Camera can\'t be deleted since it\'s being used in a camera configuration. You\'ll need to delete that camera configuration first.", "error")
            return True

        return super(ModelView, self).handle_view_exception(exc)