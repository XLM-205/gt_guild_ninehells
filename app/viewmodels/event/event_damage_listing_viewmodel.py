from  datetime import datetime
from typing import List
from uuid import UUID
from app.models.enums.event_types import EventTypeEnum
from app.viewmodels.event.event_listing_viewmodel import EventListingViewModel
from app.viewmodels.member.member_damage_viewmodel import MemberDamageViewModel


class EventDamageListingViewModel(EventListingViewModel):
    event_name: str
    event_position: int
    event_type: EventTypeEnum
    event_damage: int
    event_average_damage: int
    event_start_date: datetime
    event_end_date: datetime
    event_last_position: int
    event_last_damage: int
    event_last_average_damage: int
    event_last_start_date: datetime
    event_last_end_date: datetime
    event_last_id: UUID
    exists = False
    
    
    def __init__(self, get_event_data_and_before_same_type_as_query) -> None:
        if get_event_data_and_before_same_type_as_query is None or get_event_data_and_before_same_type_as_query == (): 
            return
        self.event_name = get_event_data_and_before_same_type_as_query[0]
        self.event_position = get_event_data_and_before_same_type_as_query[1]
        self.event_type = get_event_data_and_before_same_type_as_query[2]
        self.event_damage = get_event_data_and_before_same_type_as_query[3]
        self.event_average_damage = get_event_data_and_before_same_type_as_query[4]
        self.event_start_date = get_event_data_and_before_same_type_as_query[5]
        self.event_end_date = get_event_data_and_before_same_type_as_query[6]
        self.event_last_position = get_event_data_and_before_same_type_as_query[7]
        self.event_last_damage = get_event_data_and_before_same_type_as_query[8]
        self.event_last_average_damage = get_event_data_and_before_same_type_as_query[9]
        self.event_last_start_date = get_event_data_and_before_same_type_as_query[10]
        self.event_last_end_date = get_event_data_and_before_same_type_as_query[11]
        self.event_last_id = get_event_data_and_before_same_type_as_query[12]
        self.exists = True
    
            