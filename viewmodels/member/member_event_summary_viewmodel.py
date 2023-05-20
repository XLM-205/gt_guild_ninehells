from datetime import datetime
from uuid import UUID

from models.enums.event_types import EventTypeEnum

class MemberEventSummaryViewModel:
    event_id: UUID
    event_name: str
    event_type: EventTypeEnum
    member_damage: int
    event_average: int
    event_damage: int
    event_position: int
    event_start_date: datetime
    event_end_date: datetime
    event_duration: int
    member_damage_difference: int = 0
    member_damage_ratio: float
    event_damage_ratio: float
    
    def __init__(self, member_event_summary) -> None:
        self.event_name = member_event_summary[0]
        self.event_id = member_event_summary[1]
        self.event_type = member_event_summary[2]
        self.member_damage = member_event_summary[3]
        self.event_average = member_event_summary[4]
        self.event_damage = member_event_summary[5]
        self.event_position = member_event_summary[6]
        self.event_start_date = member_event_summary[7]
        self.event_end_date = member_event_summary[8]
        
        self.event_duration = (self.event_end_date - self.event_start_date).days
        self.event_damage_ratio = (self.event_damage - self.member_damage) / self.event_damage
        self.member_damage_ratio = 1.0 - self.event_damage_ratio
    
    def compute_difference(self, against) -> None:
        self.member_damage_difference = self.member_damage - against.member_damage
