from http import HTTPStatus
from services.fetchers.fetch_raid_detailed_data import fetch_raid_detailed_data
from services.fetchers.fetch_raid_list_data import fetch_raid_list_data
from services.login import logged_user
from flask import render_template, Blueprint
from flask_login import login_required


raid = Blueprint("raid", __name__)

@raid.route("/details/<uuid:event_id>", methods=['GET'])
@login_required
def detailed(event_id):
    return render_template("event-detailed.j2", username=logged_user.name, user_id=logged_user.id, data=fetch_raid_detailed_data(event_id)), HTTPStatus.OK

@raid.route("/raid", methods=["GET"])
@login_required
def raid_page():
    return render_template("raid-list.j2", username=logged_user.name, data=fetch_raid_list_data()), HTTPStatus.OK