from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

db = SQLAlchemy()


class Membro(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_cargo = db.Column(db.Integer)
    uid = db.Column(db.String(5), unique=True)
    nome = db.Column(db.String(100))
    webpass = db.Column(db.String())
    data = db.Column(db.Date)
    ativo = db.Column(db.Boolean)
    notas = db.Column(db.String())

    @classmethod
    def authenticate(cls, identifier, webpass):
        """
        Returns a full user object if the (identifier matches the name OR uid) AND webpass matches
        :param identifier: Either the name or UID of the user
        :param webpass: The webpassword
        """
        stmt = text(f"SELECT * FROM authenticate('{identifier}', '{webpass}');")
        return cls.query.from_statement(stmt).first()

    def fetch_total_raid_damage(self):
        return query_total_damage_of(self.id, 1)
        # return query_total_damage_of(99, 1)

    def fetch_event_detailed(self):
        return query_events_detailed_user(self.id)
        # return query_events_detailed_user(99)

    def fetch_event_last_difference(self, reference_event_id: int):
        return query_event_last_difference_user(self.id, reference_event_id)
        # return query_event_last_difference_user(99, reference_event_id)


def query_total_damage_of(identifier: int, event_id: id):
    """
    Queries an user's total damage and amount of events attended for the given event id
    :param identifier: User's ID
    :param event_id: Event's ID
    :return: A Tuple that contains (<User total damage for the giving event>, <Total events attended>)
    or (0, 0) if there are no entries
    """
    cmd = text(f"SELECT * FROM GetTotalDamage({identifier}, {event_id});")
    damage_data = db.session.execute(cmd).first()
    if damage_data is None or damage_data == ():
        return 0, 0
    else:
        return damage_data


def query_events_detailed_user(user_id: int):
    """
    Queries all events details of this user and some information about said events, too
    :param user_id: User's ID
    :return: A Tuple that contains on [0]- Raid details, [1] - Mining details. Each entry have
    (0- User ID, 1- Event ID, 2- Event type, 3- User damage, 4- average damage, 5- total damage, 6- rank position,
    7- event's name, 8- when the event ended, 9- User's Damage difference from last, 10- Guild's Damage Proportion,
    11- User's Damage Proportion) in order of newest first
    (filtering that, if a Null is found, it's replaced with 0)
    or a list with two empty lists inside if there are no entries
    """
    cmd = text(f"SELECT * FROM GetAllEventsDetailed WHERE id_membro = {user_id} ORDER BY id_evento DESC;")
    event_data = db.session.execute(cmd).all()
    events = [[], []]
    if event_data is None or event_data == []:
        return events
    else:
        query_length = len(event_data)
        for i in range(query_length):    # For every event...
            check_replace = []
            for entry in event_data[i]:     # ...on every index of it...
                if entry is None:
                    entry = 0
                check_replace.append(entry)
            this_damage = event_data[i][3]
            this_type = event_data[i][2]
            dif_damage = 0
            # Getting the user damage difference from the last event of the same type
            for j in range(i + 1, query_length):
                if event_data[j][2] == this_type:
                    dif_damage = this_damage - event_data[j][3]
                    break
            # Additional values
            check_replace.append(dif_damage)    # User's damage difference
            if check_replace[5] == 0:           # Preventing a division by 0
                check_replace.append(0.0)
                check_replace.append(0.0)
            else:
                check_replace.append(round((check_replace[5] - check_replace[3]) / check_replace[5] * 100, 1))
                check_replace.append(round(check_replace[3] / check_replace[5] * 100, 1))
            event_data[i] = tuple(check_replace)
            events[event_data[i][2] - 1].append(event_data[i])
        return events


def query_event_detailed(event_id: int):
    """
    Queries a specific event details
    :param event_id: The event's ID
    :return: A Tuple that contains
    [0] A list with each user's name and damage (User ID, User damage) or None if data doesn't exists for that ID
    [1-6] Event's average damage, total damage, rank position, name, when the it ended and type (raid / mining)
    Ordered by damage (Higher to Lower)
    """
    cmd = text(f"SELECT GetMembroNamed(id_membro), * FROM GetAllEventsDetailed WHERE id_evento = {event_id} "
               f"ORDER BY dano DESC;")
    event_types = ["RAID", "Mining Operations"]
    unk_event = "Unknown"
    entry = ()
    out = []
    raid_data = db.session.execute(cmd).all()
    if raid_data is None or raid_data == []:
        return [], 0, 0, 0, "Event doesn't exist", "--/--/----", unk_event
    # Filtering against null values
    for i in range(len(raid_data)):
        check_replace = []
        for entry in raid_data[i]:
            if entry is None:
                entry = 0
            check_replace.append(entry)
        raid_data[i] = tuple(check_replace)

    for entry in raid_data:
        out.append((entry[0], entry[4]))
    if 0 < entry[3] <= len(event_types):
        event_type = event_types[entry[3] - 1]
    else:
        event_type = unk_event
    return out, entry[5], entry[6], entry[7], entry[8], entry[9], event_type


def query_event_last_difference(event_id: int) -> (int, int, int, int):
    """
    Returns the difference between this and the last event
    :param event_id: The event's ID
    :return: The event's rank, the difference in damage total, average and 10%, between it and the latest event of the
    same type as 'event_id'. If there are no difference, (0, 0, 0, 0) is returned
    """
    cmd = text(f"SELECT * FROM GetEventLatestDiferenceSameAs({event_id});")
    dif = db.session.execute(cmd).first()
    if dif is None or dif[0] is None:
        return 0, 0, 0, 0
    else:
        return dif


def query_event_last_difference_user(user_id: int, event_id: int) -> int:
    """
    Returns the difference from the last event of same type for the given user
    :param user_id: User's ID
    :param event_id: Event's ID
    :return: The user's difference in damage from the latest event of the same type as 'event_id'.
    If there are no difference, 0 is returned
    """
    cmd = text(f"SELECT dif FROM GetEventDetailedWithDiference({event_id}) WHERE membro_id = {user_id};")
    dif = db.session.execute(cmd).first()
    if dif is None or dif == ():
        return 0
    else:
        return dif[0]


def query_progression_guild():
    """
    Queries all raids registered
    :return: A list with 0- Raid ID, 1- Event Type (unused), 2- Total Damage, 3- Average Damage, 4- 10% Threshold,
    5- Start Date, 6- End Date, 7- Rank Position, 8- Raid Name, replacing null values with 0 or "", in order of newest
    first. If there are no entries, return an empty list
    """
    cmd = text(f"SELECT * FROM Evento WHERE id_tipo = 1 ORDER BY id DESC;")
    raid_data = db.session.execute(cmd).all()
    if raid_data is None or raid_data == []:
        return []
    # Filtering against null values
    for i in range(len(raid_data)):
        check_replace = []
        for entry in raid_data[i]:
            if entry is None:
                entry = 0
            check_replace.append(entry)
        raid_data[i] = tuple(check_replace)
    return raid_data


def query_progression_user(user_id: int):
    """
    Queries all raids registered for the giving user
    :param user_id: User's ID
    :return: A list with 0- Member ID, 1- Event ID, 2- User's Damage, 3- Average Guild Damage on the raid,
     4- Guild's Total Damage, 5- Rank position, 6- Raid Name, 7- End Date in order of newest
    first. If there are no entries, return an empty list
    """
    cmd = text(f"SELECT * FROM GetRaidDetailed WHERE id_membro = {user_id} ORDER BY id_evento DESC;")
    raid_data = db.session.execute(cmd).all()
    if raid_data is None or raid_data == []:
        return []
    else:
        return raid_data
