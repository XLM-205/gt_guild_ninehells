from typing import List, Tuple
from uuid import UUID

from app.db.db import db
from sqlalchemy import text
from app.models.enums.event_types import EventTypeEnum
from app.viewmodels.event.event_damage_listing_viewmodel import EventDamageListingViewModel
from app.viewmodels.event.event_listing_viewmodel import EventListingViewModel
from app.viewmodels.event.event_summary_viewmodel import EventSummaryViewModel
from app.viewmodels.member.member_damage_difference_viewmodel import MemberDamageDifferenceViewModel
from app.viewmodels.member.member_event_summary_viewmodel import MemberEventSummaryViewModel


def query_all_events_detailed_for_member(member_id: UUID) -> List[List[MemberEventSummaryViewModel]]:     
    """ Queries all events details of this user and some information about said events, too
    
    Args:
        member_id: Member's Id
        
    Returns: A List that contains an entry for each event type, following the 'event_types' enum details. 
        Each index of the List is a 'MemberEventSummary' Object
    """
    cmd = text(f"SELECT * FROM GetMemberEventSummary('{member_id}') ORDER BY endDate DESC;")
    event_data = db.session.execute(cmd).all()
    events = []
    for i in range(len(EventTypeEnum)):
        events.append([])
    if event_data is None or event_data == []:
        return events
    else:
        query_length = len(event_data)
        for i in range(query_length):    # For every event...
            event_type = event_data[i][2]
            events[event_type].append(MemberEventSummaryViewModel(event_data[i]))
            
        for i in range(len(EventTypeEnum)):
            if len(events[i]) > 1:
                for j in range(len(events[i]) - 2, -1, -1):
                    events[i][j].compute_difference(events[i][j+1])
                
        return events


def query_event_detailed_with_difference(event_id: UUID) -> List[MemberDamageDifferenceViewModel]:
    """ Queries the list of members and their damages on `event_id` event
    Args:
        event_id: The event's ID
    Returns: A List of `MemberDamageDifferenceViewModel`
    """
    cmd = text(f"SELECT * FROM GetEventDetailedWithDifference('{event_id}')")
    member_data = db.session.execute(cmd).all()
    members: List[MemberDamageDifferenceViewModel] = []
    for member in member_data:
        members.append(MemberDamageDifferenceViewModel(member[0], member[1], member[2], member[3]))
    return members
    

def query_event_data_and_before_same_type_as(event_id: UUID) -> EventDamageListingViewModel:
    """ Queries the a particular event's data and the difference of the previous event of the same type.
    Args:
        event_id: The event's ID
    Returns: A `EventDamageListingViewModel`. If there are no events previous to this one, all `last` members will be the same as is
    """
    cmd = text(f"SELECT * FROM GetEventDataAndBeforeSameTypeAs('{event_id}')")
    return EventDamageListingViewModel(db.session.execute(cmd).first())


def query_total_damage_of_event_type(event_type: EventTypeEnum) -> Tuple[int, int]:
    """ Returns the sum amount of damage, and the amount of events, for the given 'event_type'

    Args:
        event_type (EventTypeEnum): The event type

    Returns:
        Tuple[int, int]: A tuple of [sum of all damages, amount of events]
    """    
    cmd = text(f"SELECT * FROM GetTotalDamageOfEventType({event_type});")
    totals = db.session.execute(cmd).first()
    if totals is None or totals == ():
        return (0, 0)
    return (totals[0], totals[1])


def query_event_last_difference(event_id: int) -> Tuple[int, int, int, int]:
    """ Returns the difference between this and the last event
    
    Args:
        event_id: The event's ID
        
    Returns: 
        The event's rank, the difference in damage total, average and 10%, between it and the latest event of the
    same type as 'event_id'. If there are no difference, (0, 0, 0, 0) is returned
    """
    #TODO: Fix call. Maybe get this info from a previous query
    cmd = text(f"SELECT * FROM GetEventLatestDifferenceSameAs({event_id});")
    dif = db.session.execute(cmd).first()
    if dif is None or dif[0] is None:
        return 0, 0, 0, 0
    else:
        return dif


def query_event_last_difference_member(member_id: UUID, event_id: UUID) -> int:
    """
    Returns the difference from the last event of same type for the given user
    :param member_id: User's ID
    :param event_id: Event's ID
    :return: The user's difference in damage from the latest event of the same type as 'event_id'.
    If there are no difference, 0 is returned
    """
    cmd = text(f"SELECT difference FROM GetEventDetailedWithDifference('{event_id}') WHERE memberId='{member_id}';")
    dif = db.session.execute(cmd).first()
    if dif is None or dif == ():
        return 0
    else:
        return dif[0]

def query_guild_event_summary(event_type: EventTypeEnum) -> List[EventSummaryViewModel]:
    """ Queries all events that match `event_type`
    Returns:
        A list of `EventSummaryViewModel`
    """
    cmd = text(f"SELECT * FROM GetEventSummaryByType({event_type})")
    summaries: List[EventSummaryViewModel] = []
    event_summaries = db.session.execute(cmd).all()
    for summary in event_summaries:
        summaries.append(EventSummaryViewModel(summary))
    return summaries

def query_guild_event_listing(event_type: EventTypeEnum) -> List[EventListingViewModel]:
    """ Queries all events that match `event_type`. A more complete query version of `query_guild_event_summary()`
    Returns:
        A list of `EventListingViewModel`
    """
    cmd = text(f"SELECT * FROM GetEventListingByType({event_type})")
    event_listings: List[EventListingViewModel] = []
    events = db.session.execute(cmd).all()
    for event in events:
        event_listings.append(EventListingViewModel(event_type, event))
    return event_listings