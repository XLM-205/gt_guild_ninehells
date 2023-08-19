
from datetime import datetime
from typing import List
from models.enums.event_types import EventTypeEnum
from services.login import logged_user

from db.queries.event_queries import query_guild_event_listing, query_total_damage_of_event_type
from viewmodels.event.event_listing_viewmodel import EventListingViewModel
from viewmodels.member.member_event_summary_viewmodel import MemberEventSummaryViewModel


def fetch_raid_list_data():
    # Query all events
    member_raid_details: List[MemberEventSummaryViewModel] = logged_user.fetch_all_events()[0][::-1]
    #member_event_details[0] = []
    guild_raid_listings: List[EventListingViewModel] = query_guild_event_listing(EventTypeEnum.Raid)
    
    # # Damage and graph data
    # member_attendances = 0
    member_total_damage = 0
    # member_all_average = 0
    member_daily_average = 0
    
    member_labels: List[str] = []
    member_damage: List[int] = []
    member_average: List[int] = []
    
    guild_labels: List[str] = []
    guild_damage: List[int] = []
    guild_average: List[int] = []
    
    # # Preparing member's personal raid data
    member_attendances = len(member_raid_details)
    guild_total_raid_damage, guild_total_raid_count = query_total_damage_of_event_type(EventTypeEnum.Raid)
    
    # # Preparing guild raid summary
    counter = 0
    for raid in guild_raid_listings:
        if raid.total_damage == 0 or raid.total_damage == None:    # If no raid damage, skip it
            continue
        guild_labels.append(raid.start_date.strftime("%d/%b/%Y"))
        guild_damage.append(raid.total_damage)
        guild_average.append(raid.average_damage)
        
        if raid.end_date == member_raid_details[counter].event_end_date:
            member_total_damage += member_raid_details[counter].member_damage
            member_daily_average += member_raid_details[counter].member_damage / member_raid_details[counter].event_duration
            member_labels.append(member_raid_details[counter].event_start_date.strftime("%d/%b/%Y"))
            member_average.append(int(member_raid_details[counter].member_damage / member_raid_details[counter].event_duration))
            member_damage.append(member_raid_details[counter].member_damage)
            counter += 1
        else:
            member_damage.append(0)
            
    guild_total = sum(guild_damage)
    
    # # 
    # for i in range(member_attendances):
    #     member_total_damage += member_raid_details[i].member_damage
    #     member_daily_average += member_raid_details[i].member_damage / member_raid_details[i].event_duration
    #     member_labels.append(member_raid_details[i].event_start_date.strftime("%d/%b/%Y"))
    #     member_average.append(int(member_raid_details[i].member_damage / member_raid_details[i].event_duration))
    #     member_damage.append(member_raid_details[i].member_damage)
        
    # for i in range(member_attendances, len(guild_raid_listings)):
    #     member_damage.append(0)
    
    if member_attendances > 0:
        # member_all_average = int(member_total_damage / member_attendances)
        member_daily_average = int(member_daily_average / member_attendances)

    data = {
        "admission_date": logged_user.admissiondate.strftime("%d/%b/%Y"),
        "days_since_admission": (datetime.today().date() - logged_user.admissiondate).days,
        # "member_total_damage": member_total_damage,
        # "member_all_average": member_all_average,
        # "member_daily_average": member_daily_average,
        "attendances": member_attendances,
        "guild_total_damage": guild_total_raid_damage,
        "guild_total_raids": guild_total_raid_count,
        "raid_listings": member_raid_details[::-1],
        "progress_guild": {
            "labels": guild_labels, "damages": guild_damage, "averages": guild_average
        },
        "progress_member": {
            "labels": member_labels, "damages": member_damage, "averages": member_average,
        },
    }
    return data