import os
import requests

from config.app_configs import app_configs
from datetime import datetime
from models.enums.severities import SeveritiesEnum
from services.login import logged_user

def send_to_webhook(message: str = "Empty Message", ping_administration: bool = False) -> None:
    if app_configs["USE_HOOK"] and os.environ.get("WEBHOOK") is not None:
        hook_url = os.environ["WEBHOOK"]
        admin_role = os.environ["ADMIN_ROLE"]
        prefix = "" if ping_administration is False else f":warning: <@&{admin_role}> "
        # Discord Hook Documentation: https://discord.com/developers/docs/resources/webhook
        discord_hook = {
            "id": "Website Hook",
            "type": 1,
            "content": f"{prefix}[{datetime.today().strftime('%d/%b/%Y %H:%M:%S')}][{logged_user.name}] > {message}",
        }
        requests.post(hook_url, json=discord_hook)