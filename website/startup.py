import os

from web_boot import create_app
from web_config import website_config, defaults, print_verbose
from log_services import logger_logout
from signal_manager.manager import SignalManager


def sigterm_catcher():
    print_verbose(sender=__name__, message=f"Intercepted a SIGTERM", color="red")
    print("SIGTERM Caught")


def sigint_catcher():
    print_verbose(sender=__name__, message=f"Intercepted a SIGINT", color="red")
    print("SIGINT Caught")


def sigabrt_catcher():
    print_verbose(sender=__name__, message=f"Intercepted a SIGABRT", color="red")
    print("SIGABRT Caught")


def sigfpe_catcher():
    print_verbose(sender=__name__, message=f"Intercepted a SIGFPE", color="red")
    print("SIGFPE Caught")


def set_config():
    SignalManager.set_callback("SIGTERM", sigterm_catcher)
    SignalManager.set_callback("SIGINT", sigint_catcher)
    SignalManager.set_callback("SIGABRT", sigabrt_catcher)
    SignalManager.set_callback("SIGFPE", sigfpe_catcher)
    website_config["VERBOSE"] = True


def main():
    global app
    set_config()
    host = "0.0.0.0"
    port = int(os.environ.get("PORT", defaults["FALLBACK"]["PORT"]))
    app = create_app()
    app.run(host=host, port=port, use_reloader=False)
    logger_logout()


if __name__ == "__main__":
    main()
else:
    set_config()
    app = create_app()
    logger_logout()
