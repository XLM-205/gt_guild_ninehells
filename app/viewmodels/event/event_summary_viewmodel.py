from datetime import datetime


class EventSummaryViewModel:
    name: str
    start_date: datetime
    total_damage: int
    average_damage: int
    
    def __init__(self, get_event_summary_by_type_query) -> None:
        if get_event_summary_by_type_query is None or get_event_summary_by_type_query == (): 
            return
        self.name = get_event_summary_by_type_query[0]
        self.start_date = get_event_summary_by_type_query[1]
        self.total_damage = get_event_summary_by_type_query[2]
        self.average_damage = get_event_summary_by_type_query[3]
            