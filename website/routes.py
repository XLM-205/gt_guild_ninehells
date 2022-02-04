import os
from datetime import datetime

import flask
import requests
from flask import render_template, Blueprint, request, url_for
from flask_login import login_required, current_user, logout_user
from werkzeug.utils import redirect

from models import query_event_detailed, query_event_last_difference, query_progression_guild, \
    query_latest_announcement, Membro, query_send_request, query_change_webpass
from security import attempt_login
from web_config import website_config

auth = Blueprint("auth", __name__)
main = Blueprint("main", __name__)


def send_to_webhook(msg: str = "Empty Message"):
    if website_config["USE_HOOK"] and os.environ.get("WEBHOOK") is not None:
        tgt = os.environ["WEBHOOK"]
        # Discord Hook Documentation: https://discord.com/developers/docs/resources/webhook
        discord_hook = {
            "id": "Website Hook",
            "type": 1,
            "content": f"[{datetime.today().strftime('%m/%b/%Y %H:%M:%S.%f')}][{current_user.nome}] > {msg}",
        }
        requests.post(tgt, json=discord_hook)


def prepare_stats_data() -> dict:
    # List order: [0]- Raid | [1]- Meteor
    event_dur = [14, 7]     # Duration, in days, of each event
    # Query all events
    event_details = current_user.fetch_event_detailed()
    # Valid events
    valid_events = [[], []]
    guild_raid_details = query_progression_guild()[::-1]
    attendances = [len(event_details[0]), len(event_details[1])]
    # Damage and graph data
    total_dmg = [0, 0]
    global_avg = [0, 0]
    daily_avg = [0, 0]
    user_labels = [[], []]
    user_values = [[], []]
    user_avg = [[], []]
    user_names = [[], []]
    guild_labels = []
    guild_values = []
    guild_avg = []
    guild_names = []
    for raid in guild_raid_details:
        if raid[2] == 0:    # If no raid damage, skip it
            continue
        guild_labels.append(raid[6].strftime("%m/%b/%Y"))
        guild_values.append(raid[2])
        guild_avg.append(raid[3])
        guild_names.append(raid[8])
    guild_total = sum(guild_values)
    # Data regarding raids
    for raids in event_details[0][::-1]:
        if raids[3] == 0:
            attendances[0] -= 1
            continue
        total_dmg[0] += raids[3]
        daily_avg[0] += raids[3] / event_dur[0]
        user_labels[0].append(raids[8].strftime("%m/%b/%Y"))
        user_avg[0].append(raids[4])
        user_names[0].append(raids[7])
        user_values[0].append(raids[3])
        valid_events[0].append(raids)
    global_avg[0] = int(total_dmg[0] / attendances[0])
    daily_avg[0] = int(daily_avg[0] / attendances[0])
    # Data regarding meteors
    for meteors in event_details[1][::-1]:
        if meteors[3] == 0:
            attendances[1] -= 1
            continue
        total_dmg[1] += meteors[3]
        daily_avg[1] += meteors[3] / event_dur[1]
        user_labels[1].append(meteors[8].strftime("%m/%b/%Y"))
        user_avg[1].append(meteors[4])
        user_names[1].append(meteors[7])
        user_values[1].append(meteors[3])
        valid_events[1].append(meteors)
    global_avg[1] = int(total_dmg[1] / attendances[1])
    daily_avg[1] = int(daily_avg[1] / attendances[1])
    data = {
        "join_date": (current_user.data.strftime("%m/%b/%Y"),
                      (datetime.today().date() - current_user.data).days),
        "total_damage": total_dmg,
        "global_avg": global_avg,
        "daily_avg": daily_avg,
        "raid_attendances": attendances[0],
        "mine_attendances": attendances[1],
        "raid_data": event_details[0],
        "mine_data": event_details[1],
        "progress_guild": {"labels": guild_labels, "values": guild_values, "avg": guild_avg, "names": guild_names,
                           "total": guild_total},
        "progress_user": {"labels": user_labels, "values": user_values, "avg": user_avg, "names": user_names,
                          # "percent_guild": round((guild_total - total_dmg[0]) / guild_total * 100, 1),
                          # "percent_self": round(total_dmg[0] / guild_total * 100, 1)
                          },
    }
    return data


# Routes > Main --------------------------------------------------------------------------------------------------------
@main.route("/", methods=['GET'])
@login_required
def index():
    return redirect(url_for('main.dashboard'))


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
    return render_template("detailed.html", username=current_user.nome, data=data), 200


@main.route("/profile", methods=['POST'])
@login_required
def profile_page_post():
    post_type = request.form.get("type")
    if post_type == "password":      # Changing the password
        cur_pass = request.form.get("passCurrent")
        new_pass = request.form.get("passNew")
        conf_pass = request.form.get("passConfirm")
        if new_pass == "" or conf_pass == "" or new_pass != conf_pass:
            flask.flash("Confirmation and New password doesn't match")
            return redirect(url_for('main.profile_page'))
        pass_exists = Membro.authenticate(current_user.uid, cur_pass)
        if pass_exists is None or pass_exists == ():
            flask.flash("Current password doesn't match")
            return redirect(url_for('main.profile_page'))
        query_change_webpass(current_user.id, new_pass)
        send_to_webhook("Changed their password successfully")
    elif post_type == "request":     # Send a request
        req = request.form.get("newRequest")
        query_send_request(current_user.id, req)
        send_to_webhook(f"Sent a new request:\n{req}")
    return redirect(url_for('main.profile_page'))


@main.route("/profile", methods=['GET'])
@login_required
def profile_page():
    return render_template("profiles.html", username=current_user.nome), 200


@main.route("/meteor", methods=["GET"])
@login_required
def meteor_page():
    return render_template("meteors.html", username=current_user.nome, data=prepare_stats_data()), 200


@main.route("/raid", methods=["GET"])
@login_required
def raid_page():
    return render_template("raids.html", username=current_user.nome, data=prepare_stats_data()), 200


@main.route("/dashboard", methods=['GET'])
@login_required
def dashboard():
    ann = query_latest_announcement()
    if ann == ():
        announcement = {"exist": False}
    else:
        announcement = {
            "exist": True,
            "id": ann[0],
            "user": ann[1],
            "date": ann[2],
            "text": ann[3],
            "title": ann[4],
        }
    return render_template("index.html", username=current_user.nome, announcement=announcement,
                           data=prepare_stats_data()), 200


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
