import os

from flask import Flask
from flask_sslify import SSLify
from sassutils.wsgi import SassMiddleware

from app.db.db import init_db
from app.routes.blueprints import init_blueprints
from app.services.login import init_login_manager
from app.utils.printer import print_verbose
from app.services.signal_manager import SignalManager
from app.config.app_configs import app_configs
from app.config.app_defaults import app_defaults


def sigterm_catcher() -> None:
    print_verbose(sender=__name__, message=f"Intercepted a SIGTERM", color="red")


def sigint_catcher() -> None:
    print_verbose(sender=__name__, message=f"Intercepted a SIGINT", color="red")


def sigabrt_catcher() -> None:
    print_verbose(sender=__name__, message=f"Intercepted a SIGABRT", color="red")


def sigfpe_catcher() -> None:
    print_verbose(sender=__name__, message=f"Intercepted a SIGFPE", color="red")


def set_config() -> None:
    SignalManager.set_callback("SIGTERM", sigterm_catcher)
    SignalManager.set_callback("SIGINT", sigint_catcher)
    SignalManager.set_callback("SIGABRT", sigabrt_catcher)
    SignalManager.set_callback("SIGFPE", sigfpe_catcher)
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
    if 'DYNO' in os.environ:  # Only invoke SSL if on Heroku (not local)
        SSLify(app)
    else:
        app.config["DEBUG"] = True  # If local, allow debug

    try:
        app.config["SECRET_KEY"] = os.environ["SKEY"]
    except KeyError:
        print_verbose(sender=__name__, message="Secret Key is missing!", color="red", underline=True)
        os.abort()

    init_login_manager(app)
    init_db(app)
    init_blueprints(app)
    app.wsgi_app = SassMiddleware(app.wsgi_app, {
        "app": ("static/sass", "static/css", "static/css")
    })

    print_verbose(sender=__name__, color="green", message="Initialization complete!")
    return app


if __name__ == "__main__":
    main()
else:
    set_config()
    app = build_app()
    #app.run()
