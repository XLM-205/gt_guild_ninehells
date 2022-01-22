import threading
import requests

from web_config import print_verbose, defaults, website_config

# We need to keep the session alive to used a logged client on the log service
logger_session = requests.Session()
# Logger credentials
log_cred = {"user": defaults["INTERNAL"]["WEB_NAME"], "webpass": None}
# Logger host
log_host: str
logged_in = False


def init_log_service(webpass: str, url: str):
    global log_host, log_cred
    if webpass is not None and (url is not None and url != ""):
        log_cred["webpass"] = webpass
        log_host = url
        logger_login()
    else:
        print_verbose(sender=__name__, message="Logger Password or URL is missing! Log service disabled", color="red")
        website_config["USE_LOGGER"] = False


def log_success(comment="Not Specified", body=None):
    log_echo(severity="Success", comment=comment, body=body, color="green", underline=False)


def log_warning(comment="Not Specified", body=None):
    log_echo(severity="Warning", comment=comment, body=body, color="Yellow")


def log_attention(comment="Not Specified", body=None):
    log_echo(severity="Attention", comment=comment, body=body, color="yellow", underline=True)


def log_error(comment="Not Specified", body=None):
    log_echo(severity="Error", comment=comment, body=body, color="red")


def log_critical(comment="Not Specified", body=None):
    log_echo(severity="Critical", comment=comment, body=body, color="red", bold=True, underline=True)


def log_echo(severity="Information", comment="Not Specified", body=None, color=None, underline=False, bold=False):
    log(severity=severity, comment=comment, body=body)
    print_verbose(sender=__name__, message=comment + (f"\n\t{body}" if body is not None else ""),
                  color=color, bold=bold, underline=underline)


def log(severity="Information", comment="Not Specified", body=None, threaded=True):
    log_data = {
        "from": defaults["INTERNAL"]["ACCESS_POINT"],
        "severity": severity,
        "comment": comment,
        "body": body
    }
    if threaded:
        log_request_async(endpoint='/log', json=log_data, post=True)
    else:
        log_request(endpoint='/log', json=log_data, post=True)


def log_clear(comment="Not Specified"):
    log_data = {
        "from": defaults["INTERNAL"]["ACCESS_POINT"],
        "comment": comment
    }
    log_request_async(endpoint="/clear", json=log_data, post=True)


# noinspection PyBroadException
def log_request(endpoint: str = None, json=None, post: bool = False, log_in_out: bool = False,
                timeout: int = defaults["REQUEST"]["TIMEOUT"]):
    """
    Makes a request to the logging server provider
    :param endpoint: [Required] The endpoint this request goes to, always prefixed with the 'log_host' URL
    :param json: (Optional) JSON body to be sent with the request
    :param post: (Optional) Defines if the request is a POST or a GET (Default is GET / False)
    :param log_in_out: (Optional) If True, the request will be treated as if it's a login / logout request, as in it
    bypasses the checks if the server is logged in or not
    :param timeout: (Optional) Timeout, in seconds, to abort the current request.
    Defaults to defaults["REQUEST"]["TIMEOUT"]
    :return: The request returned from the log server provider. If it's None, then probably something went wrong with
    the request / connection / logging provider
    """
    if log_in_out is False:
        if website_config["USE_LOGGER"] is False and (logged_in is False and defaults["LOGGER"]["REQUIRE_LOGIN"]):
            return None  # Ignore this log request since the logger is disabled by the user
    if endpoint is None or endpoint == "":
        print_verbose(sender=__name__, message="Empty request ignored", color="yellow")
        return None
    req = None
    try:
        if post:
            req = logger_session.post(log_host + endpoint, json=json, timeout=timeout)
        else:
            req = logger_session.get(log_host + endpoint, json=json, timeout=timeout)
        if req is None:
            print_verbose(sender=__name__, message=f"Request timed out\n\t> '{json}'", color="red", bold=True)
    except Exception as exc:
        print_verbose(sender=__name__, message=f"Couldn't contact log server\n{str(exc)}", color="red", bold=True)
    return req


def log_request_async(endpoint: str = None, json=None, post=False):
    threading.Thread(target=log_request, args=(endpoint, json, post)).start()


def logger_login():
    global logged_in
    if defaults["LOGGER"]["REQUIRE_LOGIN"]:
        print_verbose(sender=__name__, message=f"Attempting login to Log Server...", color="yellow")
        req = log_request("/cli/login", json=log_cred, post=True, timeout=10)   # Giving extra time to wake the server
    else:
        print_verbose(sender=__name__, message=f"Logger doesn't require a login (Aborted)", color="yellow")
        return
    if req is not None:
        if req.status_code == 200:
            print_verbose(sender=__name__, message="Login Successful", color="green")
            logged_in = True
            return
        else:
            print_verbose(sender=__name__, message=f"Login Failed with code {req.status_code}", color="red")
            logged_in = False
    else:
        print_verbose(sender=__name__, message=f"Login Failed (No response)", color="red", underline=True)
        logged_in = False
    print_verbose(sender=__name__, message=f"Logging Service disabled", color="red", underline=True)


def flood_test(amount: int, batches: int = 4):
    print(f"Flooding on {log_host} on {batches} threads")
    threads = []
    i = 0
    while i < amount:
        for t in range(batches):
            msg = f"Flood test {i + 1} / {amount}"
            print_verbose(sender=__name__, message=f"[T:{t}] {msg}", color="pink")
            # log(severity="Information", comment=msg, threaded=False)
            threads.append(threading.Thread(target=log, args=("Information", msg, None, False)))
            threads[-1].start()
            i += 1
        for t in threads:
            print_verbose(sender=__name__, message=f"Waiting for {str(t)}", color="yellow")
            t.join()
            print_verbose(sender=__name__, message=f"Done", color="green")
        threads.clear()
        # log(severity="Information", comment=msg, threaded=False)


def logger_logout():
    global logged_in
    log_request("/logout")
    logged_in = False
    print_verbose(sender=__name__, message=f"Logged out from Log Server", color="yellow")
