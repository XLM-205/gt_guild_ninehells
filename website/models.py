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

    def fetch_total_damage(self):
        return query_total_damage(self.id, 1)

    def fetch_raid_detailed(self):
        return query_raid_detailed_of(self.id)


def query_total_damage(identifier: int, event_id: id):
    """
    Queries an user's total damage and amount of events attended for the given event id
    :param identifier: User's ID
    :param event_id: Event's ID
    :return: A Tuple that contains (<User total damage for the giving event>, <Total events attended>
    """
    cmd = text(f"SELECT * FROM GetTotalDamage({identifier}, {event_id});")
    return db.session.execute(cmd).first()


def query_raid_detailed_of(identifier: int):
    """
    Queries all raid details of this user and some information about said raids, too
    :param identifier: User's ID
    :return: A Tuple that contains
    (User ID, Event ID, User damage, average damage, total damage, event's position, event's name, when the event ended)
    """
    cmd = text(f"SELECT * FROM GetRaidDetailed WHERE id_membro = {identifier};")
    return db.session.execute(cmd).all()
