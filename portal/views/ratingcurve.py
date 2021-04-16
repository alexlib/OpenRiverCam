from flask_admin import expose
from models.site import Site
from flask_security import current_user

from views.general import UserModelView
from models.ratingcurve import RatingCurve, RatingPoint


class RatingCurveView(UserModelView):
    can_create = False
    can_view_details = False
    edit_template = "ratingcurve/edit.html"

    column_list = (
        "site",
        RatingCurve.id,
        RatingCurve.name,
        RatingCurve.a,
        RatingCurve.b,
        RatingCurve.h0,
    )

    form_columns = (
        RatingCurve.a,
        RatingCurve.b,
        RatingCurve.h0,
    )
    column_labels = {
        "name": "Name",
        "id": "Rating curve ID",
        "a": "a [m3/s]",
        "b": "b [-]",
        "h0": "zero flow level [m]",
    }

    column_descriptions = {
        "name": "Recognizeable name for rating curve",
        "id": "Numbered identifier of the rating curve",
        "a": "Multiplier in rating equation Q = a(h-h0)^b",
        "b": "Power in rating equation Q = a(h-h0)^b",
        "h0": "Level at which no flow occurs in rating equation Q = a(h-h0)^b",
    }

    column_formatters = dict(
        a=lambda v, c, m, p: "{:.3f}".format(m.a)
        if m.a
        else "",
        b=lambda v, c, m, p: "{:.3f}".format(m.b)
        if m.b
        else "",
        h0=lambda v, c, m, p: "{:.3f}".format(m.h0)
        if m.h0
        else "",
    )

    # Don't show rating curves for sites which are not from this user.
    def get_query(self):
        return super(RatingCurveView, self).get_query().join(Site).filter_by(user_id=current_user.id)

    # Don't allow to access a rating curves if it's not from this user.
    def get_one(self, id):
        return super(RatingCurveView, self).get_query().filter_by(id=id).join(Site).filter_by(user_id=current_user.id).one()

    @expose("/")
    def index_view(self):
        self._refresh_filters_cache()
        return super(RatingCurveView, self).index_view()
