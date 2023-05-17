import datetime
from uuid import UUID

from db.db import db
from sqlalchemy import text
from db.queries.request_queries import query_send_request


def query_change_webpass(member_id: UUID, wp: str) -> None:
    """Change the Web Password of a member. It also creates an inactive request with the current date of the change

    Args:
        member_id (uuid): Member's Id
        wp (str): The new web-password
    """    
    cmd = text(f"SELECT changeWebpass('{member_id}', '{wp}')")
    db.session.execute("COMMIT")  # Required to end past transactions
    db.session.execute(cmd)
    query_send_request(member_id, f"Changed password on {datetime.datetime.today()}", active=False)