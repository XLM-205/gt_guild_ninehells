
import json
from tkinter import EventType
import flask

from ast import Tuple
from http import HTTPStatus
from db.queries.announcement_queries import query_announcement_latest
from db.queries.event_queries import query_event_detailed_with_difference, query_event_last_difference
from db.queries.request_queries import query_send_request
from db.queries.service_queries import query_change_webpass
from models.enums.event_types import EventTypeEnum
from models.members import Members
from services.fetchers.fetch_dashboard_data import fetch_dashboard_data
from services.fetchers.fetch_raid_detailed_data import fetch_raid_detailed_data
from services.fetchers.fetch_raid_list_data import fetch_raid_list_data
from services.login import logged_user
from flask import redirect, render_template, Blueprint, request, url_for
from flask_login import login_required
from werkzeug.wrappers.response import Response

from services.hooks.webhook import send_to_webhook
from utils.formatters import format_abbreviated_number

raid = Blueprint("raid", __name__)

@raid.route("/details/<uuid:event_id>", methods=['GET'])
@login_required
def detailed(event_id):
    return render_template("event-detailed.j2", username=logged_user.name, user_id=logged_user.id, data=fetch_raid_detailed_data(event_id)), HTTPStatus.OK

@raid.route("/raid", methods=["GET"])
@login_required
def raid_page():
    return render_template("raid-list.j2", username=logged_user.name, data=fetch_raid_list_data()), HTTPStatus.OK