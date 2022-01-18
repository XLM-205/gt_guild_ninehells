import flask
import sqlalchemy
from flask import render_template, Blueprint, request, flash, url_for
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.utils import redirect
from sqlalchemy.exc import ProgrammingError

from models import Membro
from security import injection_guard, InjectionToken

auth = Blueprint("auth", __name__)
main = Blueprint("main", __name__)


# Routes > Main --------------------------------------------------------------------------------------------------------
@main.route("/")
@login_required
def index():
    return redirect(url_for('main.dashboard'))


@main.route("/dashboard")
@login_required
def dashboard():
    total_dmg = 0
    raids = current_user.fetch_raid_detailed()
    for raid in raids:
        total_dmg += raid[2]
    user_data = {
        "name": current_user.nome,
        "total_damage": f"{total_dmg:,}",
        "attendances": len(raids),
        "raid_data": raids,
    }
    return render_template("index.html", data=user_data)


# Routes > Authentication ----------------------------------------------------------------------------------------------
@auth.route("/login")
def login():
    return render_template("login.html")


@auth.route("/login", methods=["POST"])
def login_post():
    log_in = request.form.get("log_in")
    wp = request.form.get("password")
    remember = True if request.form.get("remember") else False

    try:
        injection_guard([log_in, wp])
        user = Membro.authenticate(log_in, wp)
    except InjectionToken:
        # Probable SQL Injection attack!
        # log_critical(f"SQL Injection attempt from {flask.request.remote_addr} !", {"log_in": log_in, "wp": wp})
        flash("Login information had invalid characters")
        return redirect("login")
    except sqlalchemy.exc.ProgrammingError:
        # Probable SQL Injection attack!
        # log_critical(f"SQL Injection attempt from {flask.request.remote_addr} !", {"log_in": log_in, "wp": wp})
        flash("Invalid Login")
        return redirect("login")
    except (sqlalchemy.exc.NoSuchColumnError, AttributeError, TypeError):
        flash("Invalid Login")
        return redirect("login")
    print(flask.request.remote_addr)
    if user is None:
        flash("Invalid Login")
        return redirect("login")
    login_user(user, remember=remember)
    return redirect("/")


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
