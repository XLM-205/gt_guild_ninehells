from datetime import datetime
from uuid import UUID

from app.models.enums.member_roles import MemberRoleEnum

class LoginAttemptViewModel:
    tries: int = 0
    is_locked: bool = False
    locked_until: datetime
        
    def unlock(self) -> None:
        self.tries = 0
        self.is_locked = False
        self.locked_until = datetime.now()
        
    def lock(self, until: datetime) -> None:
        self.is_locked = True
        self.locked_until = until
        
    def add_try(self) -> None:
        self.tries += 1