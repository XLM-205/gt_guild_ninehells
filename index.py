import os

from flask import Flask
from flask_sslify import SSLify

from db.db import init_db
from routes.blueprints import init_blueprints
from services.login import init_login_manager
from utils.printer import print_verbose
from services.signal_manager import SignalManager
from config.app_configs import app_configs
from config.app_defaults import app_defaults

def set_config() -> None:
    app_configs["VERBOSE"] = True


def main() -> None:
    global app
    set_config()
    host = "0.0.0.0"
    port = int(os.environ.get("PORT", app_defaults["FALLBACK"]["PORT"]))

    app = build_app()
    app.run(host=host, port=port, use_reloader=False)


def build_app() -> Flask:
    app = Flask(__name__)
    # if 'DYNO' in os.environ:  # Only invoke SSL if on Heroku (not local)
    #     SSLify(app)
    # else:
    app.config["DEBUG"] = True  # If local, allow debug

    try:
        app.config["SECRET_KEY"] = os.environ["SKEY"]
    except KeyError:
        print_verbose(sender=__name__, message="Secret Key is missing!", color="red", underline=True)
        os.abort()

    init_login_manager(app)
    init_db(app)
    init_blueprints(app)

    print_verbose(sender=__name__, color="green", message="Initialization complete!")
    return app


if __name__ == "__main__":
    main()
else:
    set_config()
    app = build_app()
    #app.run()
