from datetime import datetime
from uuid import UUID
from app.models.enums.event_types import EventTypeEnum

class EventListingViewModel:
    id: UUID
    name: str
    position: int
    event_type: EventTypeEnum
    total_damage: int
    average_damage: int
    start_date: datetime
    end_date: datetime
   
    def __init__(self, event_type: EventTypeEnum, get_event_listing_by_type) -> None:
        if get_event_listing_by_type is None or get_event_listing_by_type == (): 
            return
        self.event_type = event_type
        self.id = get_event_listing_by_type[0]
        self.name = get_event_listing_by_type[1]
        self.start_date = get_event_listing_by_type[2]
        self.end_date = get_event_listing_by_type[3]
        self.total_damage = get_event_listing_by_type[4]
        self.average_damage = get_event_listing_by_type[5]
        self.position = get_event_listing_by_type[6]
            