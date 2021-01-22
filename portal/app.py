from flask import Flask, redirect, jsonify
import flask_admin as admin
from models import *

# Create custom admin view
class MyAdminView(admin.BaseView):
    @admin.expose("/")
    def index(self):
        return self.render("myadmin.html")


class AnotherAdminView(admin.BaseView):
    @admin.expose("/")
    def index(self):
        return self.render("anotheradmin.html")

    @admin.expose("/test/")
    def test(self):
        return self.render("test.html")


# Create flask app
app = Flask(__name__, template_folder="templates")
app.debug = True

# Alternative routes
@app.route("/")
def index():
    return redirect("/portal", code=302)


@app.route("/api/sites")
def api_sites():
    return jsonify(sites=[{"name": "Site 1"}, {"name": "Site 2"}])


# Create admin interface
admin = admin.Admin(name="OpenRiverCam", template_mode="bootstrap4", url="/portal")
admin.add_view(MyAdminView(name="view1", category="Test"))
admin.add_view(AnotherAdminView(name="view2", category="Test"))
admin.init_app(app)

if __name__ == "__main__":

    # Start app
    app.run()
