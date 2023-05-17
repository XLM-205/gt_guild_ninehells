from uuid import UUID
import flask
import flask_login
from http import HTTPStatus

from typing import List, Tuple, Dict, Union
from datetime import datetime, timedelta
from flask import Flask, flash
from flask_login import LoginManager, current_user, login_user
from sqlalchemy.exc import ProgrammingError, NoSuchColumnError
from models.members import Members
from services.injection_guard import InjectionToken, injection_guard
from config.app_defaults import app_defaults
from services.log import log_attention, log_critical, log_error, log_success, log_warning
from viewmodels.login.login_attempt_viewmodel import LoginAttemptViewModel

# Holds all ips that tried to connect "{IP}": [tries: int, locked: bool, lock_until: datetime]
# TODO A way for Gunicorn share this across all workers
login_attempts: Dict[str, LoginAttemptViewModel] = {}
logged_user: Members = current_user # type: ignore

def init_login_manager(flask_app: Flask) -> None:
    login_manager = LoginManager()
    login_manager.login_view = "auth.login" # type: ignore
    login_manager.init_app(flask_app)
    
    @login_manager.user_loader
    def load_user(user_id: UUID) -> Members:
        return Members.query.get(user_id)

def make_login(log_in, wp) -> Tuple[Members | None, str]:
    """
    Tries to login, verifying first against SQL Injection attempts
    :param log_in: The login credentials (username / server url)
    :param wp: The WebPassword
    :return: An Users object, if successful, and None if doesn't, followed by the reason:
    """
    # noinspection PyUnresolvedReferences
    try:
        injection_guard([log_in, wp])
        member = Members.authenticate(log_in, wp)
    except ProgrammingError as pe:
        log_error(comment=f"Query Failure!\n{', '.join(pe.args)}")
        flash("Something went wrong")
        return None, "Query Failure"
    except InjectionToken:
        # Probably SQL Injection attack!
        log_critical(comment=f"SQL Injection Attempt identified from {flask.request.remote_addr} !",
                     body={"log_in": log_in, "wp": wp})
        flash("Login information had invalid characters")
        return None, "Forbidden characters"
    except (NoSuchColumnError, AttributeError, TypeError) as credential_exception:
        flash("Invalid Credentials")
        log_warning(comment=f"Invalid Credentials\n{str(credential_exception)}")
        return None, "Invalid Credentials"
    except Exception as exc:
        log_critical(comment=f"Uncaught exception trying to make login\n{str(exc)}")
        return None, f"Log-in Uncaught Exception"

    if member is not None:
        return member, "Success"
    else:
        return None, "Invalid Credentials"


def attempt_login(log_in, wp, ip_address, remember=False) -> HTTPStatus:
    """
    Attempts to make a login, checking if this IP didn't have tried brute-forcing it before
    :param log_in: The login credentials (username / server url)
    :param wp: The WebPassword
    :param ip_address: Client's IP address currently attempting to login
    :param remember: If True, remember this user on the next login
    :return: A HTTP code relative to the response of the attempt.
    200 for a successful login, 401 for a failed one and 403 if locked
    """
    # Safeguarding against brute force
    global login_attempts
    try:
        if ip_address in login_attempts:     # User is known
            if login_attempts[ip_address].is_locked is False:
                # User not locked. Attempt login
                user, reason = make_login(log_in, wp)
            elif login_attempts[ip_address].locked_until <= datetime.now():
                # User is locked, but his lock have expired

                login_attempts[ip_address].unlock()
                user, reason = make_login(log_in, wp)
            else:
                # User is still locked, log this attempt and abort
                log_attention(comment=f"IP {ip_address} tried to log in while locked. "
                                      f"Lock down ends {login_attempts[ip_address].locked_until}")
                return HTTPStatus.FORBIDDEN
        else:   # User is unknown
            login_attempts[ip_address] = LoginAttemptViewModel()
            user, reason = make_login(log_in, wp)

        # Attempting login
        if user is None:
            login_attempts[ip_address].add_try()
            if login_attempts[ip_address].tries >= app_defaults["SECURITY"]["LOGIN"]["MAX_TRIES"]:  # Lock user
                lockout = datetime.now() + timedelta(seconds=app_defaults["SECURITY"]["LOGIN"]["LOCKOUT"])
                login_attempts[ip_address].lock(lockout)
                # login_attempts[ip_address][1] = True
                # login_attempts[ip_address][2] = lockout
                log_attention(comment=f"IP {ip_address} is locked until {login_attempts[ip_address].locked_until}"
                                      f" (Too many failed attempts)")
            flash("Invalid Login")
            log_warning(comment=f"IP {ip_address} failed to login with with name '{log_in}' ({reason}) "
                                f"(Attempt {login_attempts[ip_address].tries})")
            return HTTPStatus.UNAUTHORIZED
    except (TypeError, KeyError) as exc:
        log_error(comment=f"Login exception trying to login user '{log_in}': {str(exc)})")
        return HTTPStatus.BAD_REQUEST
    except Exception as exc:
        log_critical(comment=f"Uncaught exception trying to make login\n{str(exc)}")
        return HTTPStatus.BAD_REQUEST
    login_attempts[ip_address].unlock()
    # login_attempts[ip_address][0] = 0
    # login_attempts[ip_address][1] = False
    
    login_user(user, remember=remember)
    log_success(comment=f"{logged_user.name} ({ip_address}) logged in successfully")
    return HTTPStatus.OK
