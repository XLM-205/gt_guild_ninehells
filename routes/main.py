import json
import flask

from http import HTTPStatus
from db.queries.announcement_queries import query_announcement_latest
from db.queries.request_queries import query_send_request
from db.queries.service_queries import query_change_webpass
from models.members import Members
from services.fetchers.fetch_dashboard_data import fetch_dashboard_data
from services.fetchers.fetch_raid_list_data import fetch_raid_list_data
from services.login import logged_user
from flask import redirect, render_template, Blueprint, request, url_for
from flask_login import login_required
from werkzeug.wrappers.response import Response

from services.hooks.webhook import send_to_webhook

main = Blueprint("main", __name__)

@main.route("/", methods=['GET'])
@login_required
def index() -> Response:
    return redirect(url_for('main.dashboard'))


@main.route("/profile", methods=['POST'])
@login_required
def profile_page_post() -> Response:
    post_type = request.form.get("type")
    if post_type == "password":      # Changing the password
        current_password = request.form.get("passCurrent")
        new_password = request.form.get("passNew")
        confirmation_password = request.form.get("passConfirm")
        if (new_password is None or new_password == "") or (confirmation_password is None or confirmation_password == "") or new_password != confirmation_password:
            flask.flash("Confirmation and New password doesn't match")
            return redirect(url_for('main.profile_page'))
        member = Members.authenticate(logged_user.uid, str(current_password))
        if member is None:
            flask.flash("Current password doesn't match")
            return redirect(url_for('main.profile_page'))
        query_change_webpass(logged_user.id, new_password)
        send_to_webhook("Changed their password successfully")
    elif post_type == "request":     # Send a request
        request_description = request.form.get("newRequest")
        if request_description is not None:  
            query_send_request(logged_user.id, request_description)
            send_to_webhook(f"{logged_user.name} sent a new request:\n'{request_description}'", ping_administration=True)
    return redirect(url_for('main.profile_page'))


@main.route("/profile", methods=['GET'])
@login_required
def profile_page():
    return render_template("profiles.j2", username=logged_user.name), HTTPStatus.OK


@main.route("/raid", methods=["GET"])
@login_required
def raid_page():
    return render_template("raids.j2", username=logged_user.name, data=fetch_raid_list_data()), HTTPStatus.OK


@main.route("/dashboard", methods=['GET'])
@login_required
def dashboard():
    announcement = json.dumps(query_announcement_latest().__dict__)
    return render_template("dashboard.j2", username=logged_user.name, announcement=announcement, data=fetch_dashboard_data()), HTTPStatus.OK