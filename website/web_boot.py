from flask import Flask
from flask_login import LoginManager
from flask_sslify import SSLify
import os

import routes
from models import Membro, db
from log_services import init_log_service, log_success, log_critical
from web_config import print_verbose


# Functions ------------------------------------------------------------------------------------------------------------
def create_app():
    db_uri = os.environ.get("DATABASE_URL", "")
    # Fixing deprecated convention Heroku still uses
    db_uri = db_uri.replace("postgres://", "postgresql://", 1)

    app = Flask(__name__)
    if 'DYNO' in os.environ:  # Only invoke SSL if on Heroku (not local)
        SSLify(app)
    else:
        app.config["DEBUG"] = True  # If local, allow debug
        # db_uri = os.environ.get("LOCAL_DB_URL", "")
        # log_services.log_warning(f"Using Database at {db_uri.split('/')[-1]}", body=log_services.config)

    # Initialize and login into the logger service
    # init_log_service(os.environ.get("LKEY", None), os.environ.get("LOGGER_URL", defaults["LOGGER"]["PROVIDER"]))
    init_log_service(os.environ.get("LKEY", None), os.environ.get("LOGGER_URL", "https://-1"))

    # For encrypting passwords during execution
    try:
        app.config["SECRET_KEY"] = os.environ["SKEY"]
    except KeyError:
        print_verbose(sender=__name__, message="Secret Key is missing!", color="red", underline=True)
        os.abort()
    app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return Membro.query.get(int(user_id))

    app.register_blueprint(routes.auth)
    app.register_blueprint(routes.main)

    if db_uri is not None and db_uri != "":
        db.init_app(app)

    else:   # No database! Aborting...
        log_critical(comment="No database detected, aborting startup...")
        os.abort()
    log_success("Guild Website initialization complete! Starting WSGI Server...")
    return app
