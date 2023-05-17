import os
import requests

from config.app_configs import app_configs
from datetime import datetime
from services.login import logged_user

def send_to_webhook(msg: str = "Empty Message") -> None:
    if app_configs["USE_HOOK"] and os.environ.get("WEBHOOK") is not None:
        tgt = os.environ["WEBHOOK"]
        # Discord Hook Documentation: https://discord.com/developers/docs/resources/webhook
        discord_hook = {
            "id": "Website Hook",
            "type": 1,
            "content": f"[{datetime.today().strftime('%d/%b/%Y %H:%M:%S')}][{logged_user.name}] > {msg}",
        }
        requests.post(tgt, json=discord_hook)