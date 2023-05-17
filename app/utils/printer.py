import os

from app.config.app_configs import app_configs
from app.config.app_defaults import app_defaults
from datetime import datetime

def print_verbose(sender: str, message: str, color: str = "", bold: bool = False, underline: bool = False, force: bool = False) -> None:
    """
    Prints a message on the console if 'logger_config["VERBOSE"]' is True
    :param sender: The module that sent the message
    :param message: The message to be printer on the console
    :param color: A color to override the default one. Needs to be a valid color of 'print_rich'. Default is None
    :param bold: If true, prints the message in bold. Default is False
    :param underline: If true, prints the message with an underline. Default is False
    :param force: If true, prints the message regardless if the app_configs['VERBOSE'] is False. Default is False
    """
    sender_module = ""
    if sender is not None:
        sender = sender.upper()
        sender_module = f"[Module: {sender}]"
    if app_configs["VERBOSE"] or force:
        print_rich(f"[{datetime.now().strftime('%H:%M:%S.%f')}][PID: {os.getpid():04d}]{sender_module}{message}",
                   color=color, bold=bold, underline=underline)


def print_rich(message: str, color=None, bold=False, underline=False):
    """
    Prints text with color, header, bold or underline
    :param message: The message to be written
    :param color: 'black', 'red', 'green', 'yellow', 'blue', 'pink', 'cyan', or 'white'. Defaults to '' (none color)
    :param bold: bool
    :param underline: bool
    """
    # From https://stackoverflow.com/questions/287871/how-to-print-colored-text-to-the-terminal
    end = '\033[0m'
    b = '\033[1m' if bold else ''
    u = '\033[4m' if underline else ''
    palette = {
        'black': '\033[90m', 'red': '\033[91m', 'green': '\033[92m', 'yellow': '\033[93m', 'blue': '\033[94m',
        'pink': '\033[95m', 'cyan': '\033[96m', 'white': '\033[97m'
    }
    c = ''
    if color is None:
        color = ''
    else:
        color = str.lower(color)
    if color in palette:
        c = palette[color]

    print(f"{c}{b}{u}{message}{end}")
