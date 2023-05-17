from uuid import UUID
from app.models.enums.event_types import EventTypeEnum

class MemberTotalDamageViewModel:
    member_id: UUID
    event_type: EventTypeEnum
    total_damage = 0
    event_count = 0
    
    def __init__(self, member_id, event_type, get_member_total_damage_query) -> None:
        self.member_id = member_id
        self.event_type = event_type
        if get_member_total_damage_query is None or get_member_total_damage_query == (): 
            return
        self.total_damage = get_member_total_damage_query[0]
        self.event_count = get_member_total_damage_query[1]
        