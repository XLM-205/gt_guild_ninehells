from uuid import UUID
from services.login import logged_user
from db.queries.event_queries import query_event_data_and_before_same_type_as, query_event_detailed_with_difference
from utils.formatters import format_abbreviated_number


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

    return data
