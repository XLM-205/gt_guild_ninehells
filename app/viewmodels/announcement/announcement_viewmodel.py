from datetime import datetime
from uuid import UUID


class AnnouncementViewModel:
    id: UUID
    member_name: str
    create_date: datetime
    description: str
    title: str
    exists = False
    
    def __init__(self, get_latest_announcement_query) -> None:
        if get_latest_announcement_query is None or get_latest_announcement_query == (): 
            return
        self.id = get_latest_announcement_query[0]
        self.member_name = get_latest_announcement_query[1]
        self.create_date = get_latest_announcement_query[2]
        self.description =  get_latest_announcement_query[3]
        self.title = get_latest_announcement_query[4]
        self.exists = True
        