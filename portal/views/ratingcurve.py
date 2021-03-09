from flask_admin import expose
from views.general import UserView


class RatingCurveView(UserView):
    @expose("/")
    def index(self):
        return self.render("ratingcurve/index.html")
