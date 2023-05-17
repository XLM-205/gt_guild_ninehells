from typing import List
from uuid import UUID

from db.db import db
from flask_login import UserMixin
from sqlalchemy import text, UUID
from db.queries.event_queries import query_all_events_detailed_for_member, query_event_last_difference_member
from db.queries.member_queries import query_member_progression, query_member_total_damage_of_event_type
from models.enums.event_types import EventTypeEnum
from viewmodels.member.member_event_summary_viewmodel import MemberEventSummaryViewModel
from viewmodels.member.member_total_damage_viewmodel import MemberTotalDamageViewModel

class Members(UserMixin, db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.Integer)
    uid = db.Column(db.String(5), unique=True)
    webpass = db.Column(db.String())
    active = db.Column(db.Boolean)
    admissiondate = db.Column(db.Date)
    dischargedate = db.Column(db.Date)
    notes = db.Column(db.String())

    @classmethod
    def authenticate(cls, identifier: str, webpass: str):
        """Authenticate the member within the database

        Args:
            identifier (string): Either the name or UID of the member\n
            webpass (string): The password

        Returns:
            Members: A member object with their id, name, role, uid and admission date
        """
        stmt = text(f"SELECT * FROM authenticate('{identifier}', '{webpass}');")
        authenticated_member = cls.query.from_statement(stmt).first()
        if authenticated_member is None or authenticated_member == ():
            return None
        return authenticated_member

    def fetch_total_raid_damage(self) -> MemberTotalDamageViewModel:
        return query_member_total_damage_of_event_type(self.id, EventTypeEnum.Raid)

    def fetch_all_events(self) -> List[List[MemberEventSummaryViewModel]]:
        return query_all_events_detailed_for_member(self.id)

    # def fetch_event_last_difference(self, event_id: UUID):
    #     return query_event_last_difference_member(self.id, event_id)
    
    def fetch_member_progression(self) -> List[MemberEventSummaryViewModel]:
        return query_member_progression(self.id)
