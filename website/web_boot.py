from flask import Flask
from flask_login import LoginManager
from flask_sslify import SSLify
import os

import routes
from models import Membro, db
from log_services import log_cred, log_success, logger_login
from web_config import print_verbose, website_config


# Functions ------------------------------------------------------------------------------------------------------------
def init_logger():
    logger_login()
    log_success("Initialization successful!")


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

    # For encrypting passwords during execution
    try:
        # log_cred["webpass"] = os.environ["LKEY"]
        log_cred["webpass"] = os.environ.get("LKEY", 0)
    except KeyError:
        print_verbose(sender=__name__, message="Logger Password is missing! Log service disabled", color="red")
        website_config["USE_LOGGER"] = False
    try:
        # app.config["SECRET_KEY"] = os.environ["SKEY"]
        app.config["SECRET_KEY"] = os.environ.get("SKEY", 0)
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

    # else:   # No database! Aborting...
        # todo Treat no database exception
        # db_msg = "Log Server running WITHOUT Database support"
        # print_verbose(sender=__name__, message=db_msg)
        # logger_config["POST_INIT"].append((log_internal, ("Attention", db_msg)))
        # logger_config["LOGIN"] = False  # If we don't have a database, we can't login

    return app
