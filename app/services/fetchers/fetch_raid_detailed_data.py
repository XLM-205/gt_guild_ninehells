
from datetime import datetime
from uuid import UUID
from models.enums.event_types import EventTypeEnum
from services.login import logged_user
from db.queries.event_queries import query_event_data_and_before_same_type_as, query_event_detailed_with_difference, query_guild_event_summary
from utils.formatters import format_abbreviated_number
from viewmodels.member.member_event_summary_viewmodel import MemberEventSummaryViewModel


def fetch_raid_detailed_data(event_id: UUID):

    event_details = query_event_data_and_before_same_type_as(event_id)
    event_member_details = query_event_detailed_with_difference(event_id)
    
    event_type = "Raid"       
    distribution_labels = []
    distribution_values = []
    damage_label = 0
    member_damage = 0
    rank_matters = True

    sections = len(event_member_details)
    top_damage = event_member_details[0].damage
    step = int(top_damage / sections)   # [0] Because it's ordered as the higher damage first
    labels = list(range(0, top_damage, step))
    labels[-1] = top_damage
    member_list = event_member_details[::-1]
    continue_from = 0
    for dist in labels:
        count = 0
        for member in member_list[continue_from:]:
            if member.id == logged_user.id:
                member_damage = member.damage
                damage_label = dist
            if member.damage <= dist:
                count += 1
                continue_from += 1
            else:
                break

        distribution_values.append(count)
    # Filing the labels
    for dist in labels:
        distribution_labels.append(format_abbreviated_number(dist))
    # if event_member_details.event_type == EventTypeEnum.Raid:
    # elif event_member_details.event_type == EventTypeEnum.Mining:
    #     rank_matters = False
    #     for dist in labels:
    #         dist_labels.append(dist)
    data = {
        "event_rank_matters": rank_matters,
        "event_exists": event_details.exists,
        "event_member_data": event_member_details,
        "event_average": event_details.event_average_damage,
        "event_total": event_details.event_damage,
        "event_position": event_details.event_position,
        "event_name": event_details.event_name,
        "event_end_date": event_details.event_end_date,
        "event_type": event_type,
        "event_position_difference": event_details.event_position - event_details.event_last_position,
        "event_damage_difference": event_details.event_damage - event_details.event_last_damage,
        "event_average_difference": event_details.event_average_damage - event_details.event_last_average_damage,
        "distribution": {
            "labels": distribution_labels, "values": distribution_values,
            "damage_label": damage_label, "member_damage": member_damage
        },
    }


    # # List order: [0]- Raid | [1]- Meteor
    # # event_dur = [14, 7]     # Duration, in days, of each event
    # # Query all events
    # event_details = current_user.fetch_all_events()
    # # Valid events
    # #valid_events = [[], []]
    # guild_raid_details = query_guild_event_progression()[::-1]
    # # attendances = [len(event_details[0]), len(event_details[1])]
    # attendances = 0
    # # Damage and graph data
    # total_damage = 0
    # guild_average = 0
    # daily_average = 0
    
    # member_labels = []
    # member_values = []
    # member_average = []
    # member_names = []
    
    # guild_labels = []
    # guild_damage = []
    # guild_average = []
    # guild_names = []
    # for raid in guild_raid_details:
    #     if raid[2] == 0:    # If no raid damage, skip it
    #         continue
    #     guild_labels.append(raid[6].strftime("%d/%b/%Y"))
    #     guild_damage.append(raid[2])
    #     guild_average.append(raid[3])
    #     guild_names.append(raid[8])
    # guild_total = sum(guild_damage)
    # for i in range(event_details): # Follows EventTypeEnum index: 0 - Raid, 1 - Mining (unused)
    #     total_damage[i] += event_details[i].event_damage
    #     daily_average[i] += event_details[i].event_damage / event_details[i].event_duration
    #     member_labels[i].append(event_details[i].event_start_date.strftime("%d/%b/%Y"))
    #     member_average[i].append(event_details[i].member_damage / event_details[i].event_duration)
    #     member_names[i].append(event_details[i].member)
    #     member_values[i].append(event_details[i])
    # # Data regarding raids
    # for raid in event_details[0][::-1]:
    #     if raid.event_damage == 0:
    #         attendances[0] -= 1
    #         continue
        
    #     member_labels[0].append(raid.event_start_date.strftime("%d/%b/%Y"))
    #     member_average[0].append(raid[4])
    #     member_names[0].append(raid[7])
    #     member_values[0].append(raid[3])
    #     # valid_events[0].append(raid)
    # if attendances[0] > 0:
    #     guild_average[0] = int(total_damage[0] / attendances[0])
    #     daily_average[0] = int(daily_average[0] / attendances[0])
    # # Data regarding meteors
    # for meteors in event_details[1][::-1]:
    #     if meteors[3] == 0:
    #         attendances[1] -= 1
    #         continue
    #     total_damage[1] += meteors[3]
    #     daily_average[1] += meteors[3] / event_dur[1]
    #     member_labels[1].append(meteors[8].strftime("%d/%b/%Y"))
    #     member_average[1].append(meteors[4])
    #     member_names[1].append(meteors[7])
    #     member_values[1].append(meteors[3])
    #     # valid_events[1].append(meteors)
    # if attendances[1] > 0:
    #     guild_average[1] = int(total_damage[1] / attendances[1])
    #     daily_average[1] = int(daily_average[1] / attendances[1])
    # data = {
    #     "join_date": (current_user.admissiondate.strftime("%d/%b/%Y"),
    #                  (datetime.today().date() - current_user.admissiondate).days),
    #     "total_damage": total_damage,
    #     "global_avg": guild_average,
    #     "daily_avg": daily_average,
    #     "raid_attendances": attendances[0],
    #     "mine_attendances": attendances[1],
    #     "raid_data": event_details[0],
    #     "mine_data": event_details[1],
    #     "progress_guild": {
    #         "labels": guild_labels, "values": guild_damage, "avg": guild_average,
    #         "names": guild_names, "total": guild_total
    #     },
    #     "progress_user": {
    #         "labels": member_labels, "values": member_values, "avg": member_average, "names": member_names,
    #                       # "percent_guild": round((guild_total - total_dmg[0]) / guild_total * 100, 1),
    #                       # "percent_self": round(total_dmg[0] / guild_total * 100, 1)
    #     },
    # }
    return data
