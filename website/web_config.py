import os
from datetime import datetime

# Main server configurations that can changed during runtime. Default values are defined as (Dft: T / F)
website_config = {"PRE_INIT": [],        # Stuff to do before initialization
                  "POST_INIT": [],       # Stuff to do after initialization
                  "USE_LOGGER": True,    # If True, use the logger service
                  "USE_HOOK": True,      # If True, use webhooks (Discord)
                  "VERBOSE": False}

# Default values used within the server. Changing them during runtime is NOT RECOMMENDED
defaults = {"CONSOLE": {"SERVER_BOOT": "white",  # Console Color code for each module
                        "DB_MODELS": "red",
                        "ENTRY_MANAGER": "green",
                        "UTILS": "yellow",
                        "PAGING": "blue",
                        "ROUTES": "pink",
                        "SECURITY": "cyan"},
            "SECURITY": {"INJ_GUARD": {"CASES": ["--", "\')", ");"],         # If any is found in the query, reject
                                       "GROUPS": [["\'", ")"], [")", ";"]],  # If found in the order, reject
                                       "REPLACES": [["\'", "´"], ]},        # If [0] is found, replace to [1]
                         "LOGIN": {"MAX_TRIES": 5,      # Maximum amount of wrong guesses before locking the login
                                   "LOCKOUT": 3600}},
            "FALLBACK": {"PORT": 5000,      # Default port
                         "DB_URL": None},   # Default Database URL
            "REQUEST": {"TIMEOUT": 3},      # Time, in seconds, before a GET request is ignored
            "LOGGER": {"PROVIDER": "https://rdm-gen-logserver.herokuapp.com/",  # Logger url
                       "REQUIRE_LOGIN": True},                                  # The logger require a valid login?
            "INTERNAL": {"VERSION": "0.9.0",    # Server's Version
                         "ACCESS_POINT": "http://gt-ninehells-guild.herokuapp.com/",  # Website's url
                         "WEB_NAME": "GT Guild Webpage"}}    # Website's name internally and on entries


# Methods --------------------------------------------------------------------------------------------------------------
def print_verbose(sender: str, message: str, color: str = None, bold: bool = False, underline: bool = False,
                  force: bool = False):
    """
    # Prints a message on the console if 'logger_config["VERBOSE"]' is True
    :param sender: The module that sent the message. If it matches any entry on 'defaults["INTERFACE"]["CONSOLE"]' this
    message will have that defined color. If not, it will use 'printer_color'
    :param message: The message to be printer on the console
    :param color: A color to override the default one. Needs to be a valid color of 'print_rich'. Default is None
    :param bold: If true, prints the message in bold. Default is False
    :param underline: If true, prints the message with an underline. Default is False
    :param force: If true, prints the message regardless if the website_config['VERBOSE'] is False. Default is False
    """
    if sender is None:  # Abort
        return
    sender = sender.upper()
    if website_config["VERBOSE"] or force:
        printer_color = None
        if color is not None:
            printer_color = color
        elif sender in defaults["CONSOLE"]:
            # noinspection PyTypeChecker
            printer_color = defaults["CONSOLE"][sender]
        print_rich(f"[{datetime.now().strftime('%H:%M:%S.%f')}][PID: {os.getpid():04d}][Module: {sender}] {message}",
                   color=printer_color, bold=bold, underline=underline)


def print_rich(message: str, color=None, bold=False, underline=False):
    """
    Prints text with color, header, bold or underline
    :param message: The message to be written
    :param color: 'black', 'red', 'green', 'yellow', 'blue', 'pink', 'cyan', or 'white'. Defaults to '' (none color)
    :param bold: Boolean
    :param underline: Boolean
    """
    # From https://stackoverflow.com/questions/287871/how-to-print-colored-text-to-the-terminal
    end = '\033[0m'
    b = '\033[1m' if bold else ''
    u = '\033[4m' if underline else ''
    palette = {'black': '\033[90m', 'red': '\033[91m', 'green': '\033[92m', 'yellow': '\033[93m', 'blue': '\033[94m',
               'pink': '\033[95m', 'cyan': '\033[96m', 'white': '\033[97m', }
    c = ''
    if color is None:
        color = ''
    else:
        color = str.lower(color)
    if color in palette:
        c = palette[color]

    print(f"{c}{b}{u}{message}{end}")
