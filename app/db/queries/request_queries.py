import datetime
from uuid import UUID

from app.db.db import db
from sqlalchemy import text


def query_send_request(member_id: UUID, request: str, active: bool = True) -> None:
    """Sends a request

    Args:
        member_id (uuid): Member's Id
        request (str): The request message (description)
        active (bool, optional): Defines if the request is 'Active' (unread). Defaults to True.
    """    
    cmd = text(f"INSERT INTO Requests(memberId, createDate, description, active) "
               f"VALUES ('{member_id}', '{datetime.datetime.today().date()}', '{request}', {active});")
    db.session.execute("COMMIT")
    db.session.execute(cmd)
    pass
