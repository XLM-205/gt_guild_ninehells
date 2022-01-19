import flask
from flask import render_template, Blueprint, request, url_for
from flask_login import login_required, current_user, logout_user
from werkzeug.utils import redirect

from models import query_events_detailed
from security import attempt_login

auth = Blueprint("auth", __name__)
main = Blueprint("main", __name__)


# Routes > Main --------------------------------------------------------------------------------------------------------
@main.route("/", methods=['GET'])
@login_required
def index():
    return redirect(url_for('main.dashboard'))


@main.route("/details/<int:event_id>", methods=['GET'])
@login_required
def detailed(event_id):
    raid_details = query_events_detailed(event_id)
    data = {
        "user_name": current_user.nome,
        "event_rank_matters": True if raid_details[6] == "RAID" else False,
        "event_exists": True if raid_details[0] is not None and raid_details[0] != [] else False,
        "event_data": raid_details[0],
        "event_avg": raid_details[1],
        "event_total": raid_details[2],
        "event_pos": raid_details[3],
        "event_name": raid_details[4],
        "event_date": raid_details[5],
        "event_type": raid_details[6],
    }
    return render_template("detailed.html", data=data)


@main.route("/dashboard", methods=['GET'])
@login_required
def dashboard():
    total_raid_dmg = 0
    attendances = [0, 0]
    event_details = current_user.fetch_events_detailed()
    for event in event_details:
        if event[2] == 1:    # Raids
            total_raid_dmg += event[3]
            attendances[0] += 1
        elif event[2] == 2:  # Mining operations
            attendances[1] += 1
    data = {
        "user_name": current_user.nome,
        "total_damage": f"{total_raid_dmg:,}",
        "raid_attendances": attendances[0],
        "mine_attendances": attendances[1],
        "event_data": event_details,
        "data_exists": True if event_details[0] is not None and event_details[0] != [] else False,
    }
    return render_template("index.html", data=data)


# Routes > Authentication ----------------------------------------------------------------------------------------------
@auth.route("/login", methods=['GET'])
def login():
    return render_template("login.html")


@auth.route("/login", methods=["POST"])
def login_post():
    log_in = request.form.get("log_in")
    wp = request.form.get("password")
    remember = True if request.form.get("remember") else False
    code = attempt_login(log_in, wp, flask.request.remote_addr, remember=remember)
    if code == 200:
        return redirect(url_for("main.dashboard"))
    else:
        return redirect(url_for("auth.login"))


@auth.route("/logout", methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
