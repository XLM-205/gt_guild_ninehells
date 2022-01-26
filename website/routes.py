import flask
from flask import render_template, Blueprint, request, url_for
from flask_login import login_required, current_user, logout_user
from werkzeug.utils import redirect

from models import query_event_detailed, query_event_last_difference, query_progression_guild
from security import attempt_login

auth = Blueprint("auth", __name__)
main = Blueprint("main", __name__)


# Routes > Main --------------------------------------------------------------------------------------------------------
@main.route("/", methods=['GET'])
@login_required
def index():
    return redirect(url_for('main.dashboard'))


@main.route("/profile", methods=['GET'])
@login_required
def profile():
    return redirect(url_for('main.dashboard'))
    # todo: Implement profile page for sending requests and changing web-password


@main.route("/details/<int:event_id>", methods=['GET'])
@login_required
def detailed(event_id):
    raid_details = query_event_detailed(event_id)
    dist_labels = []
    dist_values = []
    user_label = 0
    user_value = 0
    rank_matters = True
    if not raid_details[0]:
        exists = False
    else:
        exists = True
        sections = len(raid_details[0])
        step = int(raid_details[0][0][1] / sections)   # [0] Because it's ordered as the higher damage first
        labels = list(range(0, raid_details[0][0][1], step))
        labels[-1] = raid_details[0][0][1]
        rev_list = raid_details[0][::-1]
        continue_from = 0
        for dist in labels:
            count = 0
            for member in rev_list[continue_from:]:
                if member[0] == current_user.nome:
                    user_value = member[1]
                    user_label = dist
                if member[1] <= dist:
                    count += 1
                    continue_from += 1
                else:
                    break

            dist_values.append(count)
        # Filing the labels
        if raid_details[6] == "RAID":
            for dist in labels:
                if dist > 1000000000:
                    dist_labels.append(f"{int(dist / 1000000000)}B")
                elif dist > 1000000:
                    dist_labels.append(f"{int(dist / 1000000)}M")
                elif dist > 1000:
                    dist_labels.append(f"{int(dist / 1000)}K")
                else:
                    dist_labels.append(dist)
        else:
            rank_matters = False
            for dist in labels:
                dist_labels.append(dist)
    data = {
        "user_name": current_user.nome,
        "event_rank_matters": rank_matters,
        "event_exists": exists,
        "event_data": raid_details[0],
        "event_avg": raid_details[1],
        "event_total": raid_details[2],
        "event_pos": raid_details[3],
        "event_name": raid_details[4],
        "event_date": raid_details[5],
        "event_type": raid_details[6],
        "event_dif": query_event_last_difference(event_id),
        "distribution": {"labels": dist_labels, "values": dist_values,
                         "user_label": user_label, "user_value": user_value},
    }
    return render_template("detailed.html", data=data), 200


@main.route("/dashboard", methods=['GET'])
@login_required
def dashboard():
    total_raid_dmg = 0
    event_details = current_user.fetch_event_detailed()
    # todo: Limit to the last 5 entries (when we have enough data for it)
    guild_raid_details = query_progression_guild()[::-1]
    attendances = [len(event_details[0]), len(event_details[1])]
    user_labels = []
    user_values = []
    user_avg = []
    user_names = []
    guild_labels = [val[6].strftime("%m/%b/%Y") for val in guild_raid_details[:-1]]
    guild_values = [val[2] for val in guild_raid_details[:-1]]
    guild_avg = [val[3] for val in guild_raid_details[:-1]]
    guild_names = [val[8] for val in guild_raid_details[:-1]]
    guild_total = sum(guild_values)
    for raids in event_details[0][::-1]:
        total_raid_dmg += raids[3]
        user_labels.append(raids[8].strftime("%m/%b/%Y"))
        user_avg.append(raids[4])
        user_names.append(raids[7])
        user_values.append(raids[3])
    data = {
        "user_name": current_user.nome,
        "total_damage": total_raid_dmg,
        "raid_attendances": attendances[0],
        "mine_attendances": attendances[1],
        "raid_data": event_details[0],
        "mine_data": event_details[1],
        "progress_guild": {"labels": guild_labels, "values": guild_values, "avg": guild_avg, "names": guild_names,
                           "total": guild_total},
        "progress_user": {"labels": user_labels, "values": user_values, "avg": user_avg, "names": user_names,
                          "percent_guild": round((guild_total - total_raid_dmg) / guild_total * 100, 1),
                          "percent_self": round(total_raid_dmg / guild_total * 100, 1)},
    }
    return render_template("index.html", data=data), 200


# Routes > Authentication ----------------------------------------------------------------------------------------------
@auth.route("/login", methods=['GET'])
def login():
    return render_template("login.html"), 200


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
