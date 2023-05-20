
from datetime import datetime
from typing import List
from app.services.login import logged_user
from app.db.queries.event_queries import query_guild_event_summary
from app.models.enums.event_types import EventTypeEnum
from app.viewmodels.member.member_event_summary_viewmodel import MemberEventSummaryViewModel


def fetch_dashboard_data() -> dict:
    # Query all events
    member_event_details: List[List[MemberEventSummaryViewModel]] = logged_user.fetch_all_events()
    # member_event_details[0] = []
    guild_raid_summaries = query_guild_event_summary(EventTypeEnum.Raid)
    
    # Damage and graph data
    member_raid_attendances = 0
    member_raid_total_damage = 0
    member_all_raids_average = 0
    member_raid_daily_average = 0
    
    member_labels: List[str] = []
    member_damage: List[int] = []
    member_average: List[int] = []
    
    guild_labels: List[str] = []
    guild_damage: List[int] = []
    guild_average: List[int] = []
    
    # Preparing member's personal raid data
    member_raid_attendances = len(member_event_details[EventTypeEnum.Raid])
    
    # Preparing guild raid summary
    for raid in guild_raid_summaries[member_raid_attendances::-1]:
        if raid.total_damage == 0 or raid.total_damage == None:    # If no raid damage, skip it
            continue
        guild_labels.append(raid.start_date.strftime("%d/%b/%Y"))
        guild_damage.append(raid.total_damage)
        guild_average.append(raid.average_damage)
    # guild_total = sum(guild_damage)
    
    for i in range(member_raid_attendances):
        member_raid_total_damage += member_event_details[EventTypeEnum.Raid][i].member_damage
        member_raid_daily_average += member_event_details[EventTypeEnum.Raid][i].member_damage / member_event_details[EventTypeEnum.Raid][i].event_duration
        member_labels.append(member_event_details[EventTypeEnum.Raid][i].event_start_date.strftime("%d/%b/%Y"))
        member_average.append(int(member_event_details[EventTypeEnum.Raid][i].member_damage / member_event_details[EventTypeEnum.Raid][i].event_duration))
        member_damage.append(member_event_details[EventTypeEnum.Raid][i].member_damage)
    
    if member_raid_attendances > 0:
        member_all_raids_average = int(member_raid_total_damage / member_raid_attendances)
        member_raid_daily_average = int(member_raid_daily_average / member_raid_attendances)
  
    data = {
        "admission_date": logged_user.admissiondate.strftime("%d/%b/%Y"),
        "days_since_admission": (datetime.today().date() - logged_user.admissiondate).days,
        "member_raid_total_damage": member_raid_total_damage,
        "member_all_raids_average": member_all_raids_average,
        "member_raid_daily_average": member_raid_daily_average,
        "raid_attendances": member_raid_attendances,
        "progress_guild": {
            "labels": guild_labels, "damages": guild_damage, "averages": guild_average
        },
        "progress_member": {
            "labels": member_labels[::-1], "damages": member_damage[::-1], "averages": member_average[::-1],
        },
    }
    return data
