import flask_admin as admin
from flask_security import current_user
from flask_admin.menu import MenuLink
from flask_admin import expose, form
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.sqla.filters import BaseSQLAFilter
from flask import redirect, url_for
from wtforms import ValidationError
import os
import utils
import uuid

# Models for CRUD views.
from models import db
from models.camera import CameraType, Camera, CameraConfig
from models.site import Site
from models.movie import Movie


class LoginMenuLink(MenuLink):
    def is_accessible(self):
        return not current_user.is_authenticated


class LogoutMenuLink(MenuLink):
    def is_accessible(self):
        return current_user.is_authenticated


class UserModelView(ModelView):
    can_view_details = True

    def is_accessible(self):
        return current_user.is_active and current_user.is_authenticated

    def _handle_view(self, name):
        if not self.is_accessible():
            return redirect(url_for("security.login"))

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


class FilterMovieBySite(BaseSQLAFilter):
    # Override to create an appropriate query and apply a filter to said query with the passed value from the filter UI
    def apply(self, query, value, alias=None):
        return query.join(Movie.config).join(CameraConfig.camera).join(Camera.site).filter(Site.id == value)

    # readable operation name. This appears in the middle filter line drop-down
    def operation(self):
        return u'equals'

    # Override to provide the options for the filter - in this case it's a list of the titles of the Client model
    def get_options(self, view):
        return [(site.id, site.name) for site in Site.query.order_by(Site.name)]

class s3UploadField(form.FileUploadField):

    def pre_validate(self, form):
        if self._is_uploaded_file(self.data) and not self.is_file_allowed(self.data.filename):
            raise ValidationError('Invalid file extension')

    def _delete_file(self, filename):
        return filename

    def populate_obj(self, obj, name):
        if self._is_uploaded_file(self.data):
            filename = self.generate_name(obj, self.data)
            filename = self._save_file(self.data, filename)
            # update filename of FileStorage to our validated name
            self.data.filename = filename
            setattr(obj, name, filename)
            setattr(obj, "file_bucket", self.base_path)

    def _save_file(self, data, filename):
        s3 = utils.get_s3()
        bucket = self.base_path

        filename, file_extension = os.path.splitext(self.data.filename)

        # Create bucket if it doesn't exist yet.
        if s3.Bucket(bucket) not in s3.buckets.all():
            s3.create_bucket(Bucket=bucket)
        else:
            raise ValidationError('Bucket already exists')

        s3.Bucket(bucket).Object('input{}'.format(file_extension)).put(Body=data.read())

        return '{}{}'.format(filename, file_extension)

class MovieView(UserModelView):
    column_list = ("config.camera.site", Movie.file_name, Movie.timestamp, Movie.actual_water_level, Movie.discharge_q50, Movie.status)
    column_labels = {"config.camera.site": "Site"}
    column_filters = [FilterMovieBySite(column=None, name='Site')]
    column_formatters = dict(
        discharge_q05=lambda v, c, m, p: "{:.3f}".format(m.discharge_q05) if m.discharge_q05 else "",
        discharge_q25=lambda v, c, m, p: "{:.3f}".format(m.discharge_q25) if m.discharge_q25 else "",
        discharge_q50=lambda v, c, m, p: "{:.3f}".format(m.discharge_q50) if m.discharge_q50 else "",
        discharge_q75=lambda v, c, m, p: "{:.3f}".format(m.discharge_q75) if m.discharge_q75 else "",
        discharge_q95=lambda v, c, m, p: "{:.3f}".format(m.discharge_q95) if m.discharge_q95 else ""
    )

    form_columns = ( "config", Movie.timestamp, 'file_name' )
    # form_columns = ( "config", Movie.timestamp, Movie.status, Movie.actual_water_level )

    form_extra_fields = {
        'file_name': s3UploadField(
            'File',
            allowed_extensions=('mkv','mpeg'),
            base_path=uuid.uuid4().hex
        )
    }

    # Need this so the filter options are always up-to-date.
    @expose('/')
    def index_view(self):
        self._refresh_filters_cache()
        return super(MovieView, self).index_view()

# Extend this view class for views which should only be available for logged in users.
class UserView(admin.BaseView):
    def can_view_details(self):
        return True

    def is_accessible(self):
        return current_user.is_active and current_user.is_authenticated

    def _handle_view(self, name):
        if not self.is_accessible():
            return redirect(url_for("security.login"))


class RatingCurveView(UserView):
    @admin.expose("/")
    def index(self):
        return self.render("ratingcurve/index.html")


class HelpView(admin.BaseView):
    @admin.expose("/")
    def index(self):
        return self.render("help/index.html")


admin = admin.Admin(name="OpenRiverCam", template_mode="bootstrap4", url="/portal")

# Login/logout menu links.
admin.add_link(LogoutMenuLink(name="Logout", category="", url="/logout"))
admin.add_link(LoginMenuLink(name="Login", category="", url="/login"))

# Generic CRUD views.
admin.add_view(UserModelView(Site, db, name="Sites", url="sites", category="Setup"))
admin.add_view(
    UserModelView(
        CameraType, db, name="Camera types", url="camera-types", category="Setup"
    )
)
admin.add_view(
    UserModelView(Camera, db, name="Cameras", url="cameras", category="Setup")
)
admin.add_view(
    CameraConfigView(
        CameraConfig,
        db,
        name="Camera configuration",
        url="camera-config",
        category="Setup",
    )
)
admin.add_view(MovieView(Movie, db, name="Movies", url="movies"))

# Custom user views.
admin.add_view(RatingCurveView(name="Rating curves", url="ratingcurves"))

# Publicly visible pages.
admin.add_view(HelpView(name="Help", url="help"))
