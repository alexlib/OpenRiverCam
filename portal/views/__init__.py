import flask_admin as admin
from flask_security import current_user
from flask_admin.menu import MenuLink
from flask_admin.contrib.sqla import ModelView
from flask import redirect, url_for

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
        return (current_user.is_active and
                current_user.is_authenticated)

    def _handle_view(self, name):
        if not self.is_accessible():
            return redirect(url_for("security.login"))

# Extend this view class for views which should only be available for logged in users.
class UserView(admin.BaseView):
    def can_view_details(self):
        return True

    def is_accessible(self):
        return (current_user.is_active and
                current_user.is_authenticated)

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
admin.add_link(LogoutMenuLink(name='Logout', category='', url="/logout"))
admin.add_link(LoginMenuLink(name='Login', category='', url="/login"))

# Generic CRUD views.
admin.add_view(UserModelView(Site, db, name="Sites", url="sites", category="Setup"))
admin.add_view(UserModelView(CameraType, db, name="Camera types", url="camera-types", category="Setup"))
admin.add_view(UserModelView(Camera, db, name="Cameras", url="cameras", category="Setup"))
admin.add_view(UserModelView(CameraConfig, db, name="Camera configuration", url="camera-config", category="Setup"))
admin.add_view(UserModelView(Movie, db, name="Movies", url="movies"))

# Custom user views.
admin.add_view(RatingCurveView(name="Rating curves", url="ratingcurves"))

# Publicly visible pages.
admin.add_view(HelpView(name="Help", url="help"))