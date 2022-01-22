import flask
import flask_login
import sqlalchemy
from datetime import datetime, timedelta
from flask import flash
from flask_login import login_user

from models import Membro
from web_config import defaults
from log_services import log_critical, log_attention, log_success, log_error, log_warning

# Holds all ips that tried to connect "{IP}": [tries: int, locked: bool, lock_until: datetime]
# TODO A way for Gunicorn share this across all workers
login_attempts = {}


class InjectionToken(Exception):
    """ Raised if the Injection Guard function detects an Injection Attempt """
    pass


def injection_guard(queries: []):
    """
    Analyses all query strings in 'queries' to prevent injection attacks in 3 phases. The last one attempts to fix them
    :param queries: List of query strings
    """
    # These tokens will reject a query if found at any time
    cases = defaults["SECURITY"]["INJ_GUARD"]["CASES"]
    # These tokens will reject a query if found in the order provided
    groups = defaults["SECURITY"]["INJ_GUARD"]["GROUPS"]
    # This tokens will be replaced to, if found
    replaces = defaults["SECURITY"]["INJ_GUARD"]["REPLACES"]
    for query in queries:
        # First pass: Common tokens
        for case in cases:
            if case in query:
                raise InjectionToken("Invalid characters detected on input string!", )
        # Second pass: Following Matching tokens
        for group in groups:
            full_match = True
            continue_from = 0
            for pair in group:
                continue_from = query.find(pair, continue_from)
                if continue_from == -1:
                    full_match = False
                    break
            if full_match:
                raise InjectionToken("Invalid characters detected on input string!", )
        # Third pass: Hard replace tokens if found
        for replace in replaces:
            query.replace(replace[0], replace[1])


def make_login(log_in, wp) -> (Membro, str):
    """
    Tries to login, verifying first against SQL Injection attempts
    :param log_in: The login credentials (username / server url)
    :param wp: The WebPassword
    :return: An Users object, if successful, and None if doesn't, followed by the reason:
    """
    # noinspection PyUnresolvedReferences
    try:
        injection_guard([log_in, wp])
        user = Membro.authenticate(log_in, wp)
    except (InjectionToken, sqlalchemy.exc.ProgrammingError):
        # Probable SQL Injection attack!
        log_critical(comment=f"SQL Injection Attempt identified from {flask.request.remote_addr} !",
                     body={"log_in": log_in, "wp": wp})
        flash("Login information had invalid characters")
        return None, "Forbidden characters"
    except (sqlalchemy.exc.NoSuchColumnError, AttributeError, TypeError):
        flash("Invalid Credentials")
        return None, "Invalid Credentials"
    except Exception as exc:
        log_critical(comment=f"Uncaught exception trying to make login\n{str(exc)}")
        return None, f"Log-in Uncaught Exception"

    if user is None:
        return None, "Invalid Credentials"
    else:
        return user, "Success"


def attempt_login(log_in, wp, ip_address, remember=False):
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
    success = 200
    bad_request = 400
    failed = 401
    locked = 403
    try:
        if ip_address in login_attempts:     # User is known
            if login_attempts[ip_address][1] is False:
                # User not locked. Attempt login
                user, reason = make_login(log_in, wp)
            elif login_attempts[ip_address][2] <= datetime.now():
                # User is locked, but his lock have expired

                login_attempts[ip_address][0] = 0
                login_attempts[ip_address][1] = False
                user, reason = make_login(log_in, wp)
            else:
                # User is still locked, log this attempt and abort
                log_attention(comment=f"IP {ip_address} tried to log in while locked. "
                                      f"Lock down ends {login_attempts[ip_address][2]}")
                return locked
        else:   # User is unknown
            login_attempts[ip_address] = [0, False, None]
            user, reason = make_login(log_in, wp)

        # Attempting login
        if user is None:
            login_attempts[ip_address][0] += 1
            if login_attempts[ip_address][0] >= defaults["SECURITY"]["LOGIN"]["MAX_TRIES"]:  # Lock user
                lockout = datetime.now() + timedelta(seconds=defaults["SECURITY"]["LOGIN"]["LOCKOUT"])
                login_attempts[ip_address][1] = True
                login_attempts[ip_address][2] = lockout
                log_attention(comment=f"IP {ip_address} is locked until {login_attempts[ip_address][2]}"
                                      f" (Too many failed attempts)")
            flash("Invalid Login")
            log_warning(comment=f"IP {ip_address} failed to login with with name '{log_in}' ({reason}) "
                                f"(Attempt {login_attempts[ip_address][0]})")
            return failed
    except (TypeError, KeyError) as exc:
        log_error(comment=f"Login exception trying to login user '{log_in}': {str(exc)})")
        return bad_request
    except Exception as exc:
        log_critical(comment=f"Uncaught exception trying to make login\n{str(exc)}")
        return bad_request
    login_attempts[ip_address][0] = 0
    login_attempts[ip_address][1] = False
    login_user(user, remember=remember)
    log_success(comment=f"{flask_login.current_user.nome} ({ip_address}) logged in successfully")
    return success
