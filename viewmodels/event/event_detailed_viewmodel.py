from typing import List
from viewmodels.event.event_listing_viewmodel import EventListingViewModel
from viewmodels.member.member_damage_viewmodel import MemberDamageViewModel


class EventDetailedViewModel:
    exists = False
    member_damage: List[MemberDamageViewModel]
    
    def __init__(self, event_id, get_event_data_query) -> None:
        if get_event_data_query is None or get_event_data_query == (): 
            return
        self.id = event_id
        self.name = get_event_data_query[0]
        self.position = get_event_data_query[1]
        self.event_type = get_event_data_query[2]
        self.total_damage = get_event_data_query[3]
        self.average_damage = get_event_data_query[4]
        self.start_date = get_event_data_query[5]
        self.end_date = get_event_data_query[6]
        self.exists = True
    
    def append_member_damages(self, get_event_detailed_query) -> None:
        if get_event_detailed_query is None or get_event_detailed_query == (): 
            return
        for entry in get_event_detailed_query:
            self.member_damage.append(MemberDamageViewModel(name=entry[0], id=entry[1], damage=entry[2]))
            