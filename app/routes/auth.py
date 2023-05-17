from http import HTTPStatus
import flask

from flask import render_template, Blueprint, request, url_for
from flask_login import login_required, logout_user
from werkzeug.utils import redirect
from werkzeug.wrappers.response import Response
from services.hooks.webhook import send_to_webhook
from services.login import attempt_login


auth = Blueprint("auth", __name__)

@auth.route("/login", methods=['GET'])
def login():
    """The login page

    Returns:
        HTML: The login page HTML
    """    
    return render_template("login.j2"), HTTPStatus.OK


@auth.route("/login", methods=["POST"])
def login_post() -> Response:
    """Attempts to login the member

    Returns:
        Response: If successful, redirects to the dashboard, otherwise, to the login page again
    """    
    log_in = request.form.get("log_in")
    password = request.form.get("password")
    remember = True if request.form.get("remember") else False
    code = attempt_login(log_in, password, flask.request.remote_addr, remember=remember)
    if code == HTTPStatus.OK:
        send_to_webhook(f"Logged in successfully")
        return redirect(url_for("main.dashboard"))
    else:
        return redirect(url_for("auth.login"))


@auth.route("/logout", methods=['GET'])
@login_required
def logout() -> Response:
    """Logs the member out

    Returns:
        Response: A redirect to the login page
    """    
    send_to_webhook("Requested a log out")
    logout_user()
    return redirect(url_for("auth.login"))
