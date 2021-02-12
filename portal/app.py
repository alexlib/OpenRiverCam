from flask import Flask, redirect, jsonify, url_for
from flask_admin import helpers as admin_helpers
from flask_security import Security, login_required, SQLAlchemySessionUserDatastore
from models import db
from models.user import User, Role
from controllers import camera_type_api, processing_api
from views import admin

# Create flask app
app = Flask(__name__, template_folder="templates")
app.register_blueprint(camera_type_api)
app.register_blueprint(processing_api)
app.debug = True
app.config['SECRET_KEY'] = 'super-secret'
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_SEND_REGISTER_EMAIL'] = False
app.config['SECURITY_PASSWORD_SALT'] = 'salt'

# Setup Flask-Security
user_datastore = SQLAlchemySessionUserDatastore(db, User, Role)
security = Security(app, user_datastore)

# Alternative routes
@app.route("/")
def index():
    return redirect("/portal", code=302)

# Create admin interface
admin.init_app(app)

@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template = admin.base_template,
        admin_view = admin.index_view,
        h = admin_helpers,
        get_url = url_for
    )

if __name__ == "__main__":

    # Start app
    app.run()
