from flask import flash
from models.site import Site
from views.general import UserModelView
from flask_security import current_user
from sqlalchemy.exc import IntegrityError

class SiteView(UserModelView):
    column_list = (
        Site.id,
        Site.name,
        Site.position_x,
        Site.position_y,
        Site.position_crs,
    )

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

    def get_query(self):
        """
        Only show sites from this user.

        :return:
        """
        return super(SiteView, self).get_query().filter(Site.user_id == current_user.id)

    def get_one(self, id):
        """
        Don't allow to access a specific site if it's not from this user.

        :param id:
        :return:
        """
        return super(SiteView, self).get_query().filter_by(id=id).filter(Site.user_id == current_user.id).one()

    def on_model_change(self, form, model, is_created):
        """
        Link site to the current logged in user on creation.

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
            if e.orig.diag.message_detail.find("bathymetry") != -1:
                flash(
                    "Site can\'t be deleted since it\'s being used by a bathymetry. You\'ll need to delete that bathymetry first.",
                    "error")
            else:
                flash(
                    "Site can\'t be deleted since it\'s being used by a camera. You\'ll need to delete that camera first.",
                    "error")
            return True

        return super(ModelView, self).handle_view_exception(exc)