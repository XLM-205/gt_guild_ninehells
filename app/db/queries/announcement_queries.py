
from app.db.db import db
from sqlalchemy import text

from app.viewmodels.announcement.announcement_viewmodel import AnnouncementViewModel

def query_announcement_latest() -> AnnouncementViewModel:
    """ Query for the latest published announcement
    
    Returns: A tuple that contains (Announcement ID, User, Date, Announcement, Title) if there are new announcements.
    If there are not, return an empty tuple
    """
    cmd = text(f"SELECT * FROM GetLatestAnnouncement;")
    return AnnouncementViewModel(db.session.execute(cmd).first())
