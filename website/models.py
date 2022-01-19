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

    def fetch_events_detailed(self):
        return query_events_detailed_user(self.id)


def query_total_damage_of(identifier: int, event_id: id):
    """
    Queries an user's total damage and amount of events attended for the given event id
    :param identifier: User's ID
    :param event_id: Event's ID
    :return: A Tuple that contains (<User total damage for the giving event>, <Total events attended>)
    """
    cmd = text(f"SELECT * FROM GetTotalDamage({identifier}, {event_id});")
    return db.session.execute(cmd).first()


def query_events_detailed_user(user_id: int):
    """
    Queries all events details of this user and some information about said events, too
    :param user_id: User's ID
    :return: A Tuple that contains
    (0- User ID, 1- Event ID, 2- Event type, 3- User damage, 4- average damage,
    5- total damage, 6- rank position, 7- event's name, 8- when the event ended) in chronological order (newest first)
    """
    cmd = text(f"SELECT * FROM GetAllEventsDetailed WHERE id_membro = {user_id} ORDER BY id_evento DESC;")
    return db.session.execute(cmd).all()


def query_events_detailed(event_id: int):
    """
    Queries a specific raid details
    :param event_id: The raid's ID
    :return: A Tuple that contains
    [0] A list with each user's name and damage (User ID, User damage) or None if data doesn't exists for that ID
    [1-6] Event's average damage, total damage, rank position, name, when the it ended and type (raid / mining)
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
    for entry in raid_data:
        out.append((entry[0], entry[4]))
    if 0 < entry[3] <= len(event_types):
        event_type = event_types[entry[3] - 1]
    else:
        event_type = unk_event
    return out, entry[5], entry[6], entry[7], entry[8], entry[9], event_type
