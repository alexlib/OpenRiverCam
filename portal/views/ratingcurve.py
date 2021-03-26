from flask import request
from flask_admin import expose
from flask_admin.model.helpers import get_mdict_item_or_list

from views.general import UserModelView
from models.ratingcurve import RatingCurve, RatingPoint


class RatingCurveView(UserModelView):
    can_create = False

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
    # TODO: def update_modelself, form, model)
    # Here make sure the "include" state of the ratingpoints is adequately stored

    @expose('/edit/', methods=('GET', 'POST'))
    def edit_view(self):
        self.edit_template = "ratingcurve/edit.html"
        id = get_mdict_item_or_list(request.args, "id")
        rating_points = RatingPoint.query.filter(RatingPoint.ratingcurve_id == id).all()
        self._template_args["ratingpoints"] = rating_points
        return super(RatingCurveView, self).edit_view()
    # Need this so the filter options are always up-to-date.
    @expose("/")
    def index_view(self):
        self._refresh_filters_cache()
        return super(RatingCurveView, self).index_view()
