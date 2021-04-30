import os
from flask import Flask, redirect, jsonify, url_for
from flask_admin import helpers as admin_helpers
from flask_security import Security, login_required, SQLAlchemySessionUserDatastore
from models import db
from models.user import User, Role
from controllers import camera_type_api, processing_api, visualize_api, bathymetry_api, ratingcurve_api
from views import admin

# Create flask app
app = Flask(__name__, template_folder="templates")
app.register_blueprint(camera_type_api)
app.register_blueprint(processing_api)
app.register_blueprint(visualize_api)
app.register_blueprint(bathymetry_api)
app.register_blueprint(ratingcurve_api)

app.debug = True
app.config["SECRET_KEY"] = os.getenv("APP_SECRET_KEY")
app.config["SECURITY_REGISTERABLE"] = (os.getenv("FLASK_ENV") != "ibmcloud")
app.config["SECURITY_SEND_REGISTER_EMAIL"] = False
app.config["SECURITY_PASSWORD_SALT"] = os.getenv("SECURITY_PASSWORD_SALT")

# Setup Flask-Security
user_datastore = SQLAlchemySessionUserDatastore(db, User, Role)
security = Security(app, user_datastore)

# Alternative routes
@app.route("/")
def index():
    return redirect("/portal", code=302)


# Create admin interface
admin.init_app(app)

# Provide necessary vars to flask-admin views.
@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
        get_url=url_for,
    )


# Resolve database session issues for the combination of Postgres/Sqlalchemy scoped session/Flask-admin.
@app.teardown_appcontext
def shutdown_session(exception=None):
    # load all expired attributes for the given instance
    db.expire_all()


if __name__ == "__main__":
    # Start app
    port = int(os.getenv("PORT", 80))
    app.run(host='0.0.0.0', port=port)
