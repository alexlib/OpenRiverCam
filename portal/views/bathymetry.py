from flask import flash
from models.bathymetry import Bathymetry, BathymetryCoordinate
from models.site import Site
from flask_security import current_user
from sqlalchemy.exc import IntegrityError
from views.general import UserModelView


class BathymetryView(UserModelView):
    column_list = (
        "site",
        Bathymetry.timestamp
    )
    form_columns = ("site", Bathymetry.timestamp)
    form_args = {
        "site": {
            "query_factory": lambda: Site.query.filter_by(
                user_id=current_user.id
            )
        }
    }

    create_template = "bathymetry/create.html"
    edit_template = "bathymetry/edit.html"
    details_template = "bathymetry/details.html"


    def get_query(self):
        """
        Don't show bathymetry for sites which are not from this user.

        :return: sqlalchemy query
        """
        return super(BathymetryView, self).get_query().join(Site).filter_by(user_id=current_user.id)

    def get_one(self, id):
        """
        Don't allow to access a specific movie if it's not from this user.

        :param id:
        :return: sqlalchemy query
        """
        return super(BathymetryView, self).get_query().filter_by(id=id).join(Site).filter_by(user_id=current_user.id).one()

    def handle_view_exception(self, e):
        """
        Human readable error message for database integrity errors.

        :param e:
        :return:
        """
        if isinstance(e, IntegrityError):
            flash("Bathymetry can\'t be deleted since it\'s being used by a movie. You\'ll need to delete that movie first.", "error")
            return True

        return super(ModelView, self).handle_view_exception(exc)
