
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


# @main.route("/details/<uuid:event_id>", methods=['GET'])
# @login_required
# def detailed(event_id):
#     event_details = query_event_detailed_with_difference(event_id)
#     dist_labels = []
#     dist_values = []
#     damage_label = 0
#     member_damage = 0
#     rank_matters = True

#     sections = len(event_details.member_damage)
#     top_damage = event_details.member_damage[0].damage
#     step = int(top_damage / sections)   # [0] Because it's ordered as the higher damage first
#     labels = list(range(0, top_damage, step))
#     labels[-1] = top_damage
#     member_list = event_details.member_damage[::-1]
#     continue_from = 0
#     for dist in labels:
#         count = 0
#         for member in member_list[continue_from:]:
#             if member.id == logged_user.id:
#                 member_damage = member.damage
#                 damage_label = dist
#             if member.damage <= dist:
#                 count += 1
#                 continue_from += 1
#             else:
#                 break

#         dist_values.append(count)
#     # Filing the labels
#     if event_details.event_type == EventTypeEnum.Raid:
#         for dist in labels:
#             dist_labels.append(format_abbreviated_number(dist))
#     elif event_details.event_type == EventTypeEnum.Mining:
#         rank_matters = False
#         for dist in labels:
#             dist_labels.append(dist)
#     data = {
#         "event_rank_matters": rank_matters,
#         "event_exists": event_details.exists,
#         "event_data": event_details.member_damage,
#         "event_avg": event_details.average_damage,
#         "event_total": event_details.total_damage,
#         "event_pos": event_details.position,
#         "event_name": event_details.name,
#         "event_date": event_details.start_date,
#         "event_type": event_details.event_type,
#         "event_dif": query_event_last_difference(event_id),
#         "distribution": {
#             "labels": dist_labels, "values": dist_values,
#             "damage_label": damage_label, "member_damage": member_damage
#         },
#     }
#     return render_template("detailed.j2", username=logged_user.name, user_id=logged_user.id, data=data), HTTPStatus.OK


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
            send_to_webhook(f"{logged_user.name} sent a new request:\n'{request_description}'")
    return redirect(url_for('main.profile_page'))


@main.route("/profile", methods=['GET'])
@login_required
def profile_page():
    return render_template("profiles.j2", username=logged_user.name), HTTPStatus.OK


# @main.route("/meteor", methods=["GET"])
# @login_required
# def meteor_page():
#     return render_template("meteors.j2", username=logged_user.name, data=prepare_stats_data()), HTTPStatus.OK


@main.route("/raid", methods=["GET"])
@login_required
def raid_page():
    return render_template("raids.j2", username=logged_user.name, data=fetch_raid_list_data()), HTTPStatus.OK


@main.route("/dashboard", methods=['GET'])
@login_required
def dashboard():
    announcement = json.dumps(query_announcement_latest().__dict__)
    return render_template("dashboard.j2", username=logged_user.name, announcement=announcement, data=fetch_dashboard_data()), HTTPStatus.OK