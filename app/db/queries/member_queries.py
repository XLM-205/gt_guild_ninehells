from typing import List
from uuid import UUID

from app.db.db import db
from sqlalchemy import text
from app.models.enums.event_types import EventTypeEnum
from app.viewmodels.member.member_event_summary_viewmodel import MemberEventSummaryViewModel
from app.viewmodels.member.member_total_damage_viewmodel import MemberTotalDamageViewModel

def query_member_total_damage_of_event_type(member_id: UUID, event_type: EventTypeEnum) -> MemberTotalDamageViewModel:
    """ Queries a member's total damage and amount of events attended for the given event id
    
    Args:
        member_id: member's ID
        event_type: Event type
        
    Returns:
        A ViewModel that contains the damage total and event count. These values defaults to 0 if member doesn't exist or there are no entries
    """
    cmd = text(f"SELECT * FROM GetMemberTotalDamage('{member_id}', {event_type});")
    return MemberTotalDamageViewModel(member_id, event_type, db.session.execute(cmd).first())

def query_member_progression(member_id: int) -> List[MemberEventSummaryViewModel]:
    """ Queries all raids registered for the giving user
    Args:
        member_id: User's ID
    Returns: 
        A List of MemberEventSummaryViewModel. If there are no entries, return an empty list
    """
    cmd = text(f"SELECT * FROM GetMemberEventSummary('{member_id}')")
    summary = []
    entries = db.session.execute(cmd).all()
    if entries is not None and len(entries) > 0:
        summary = [entry for entry in entries]

    return summary
            