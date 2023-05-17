from uuid import UUID

from models.enums.member_roles import MemberRoleEnum

class MemberDamageViewModel:
    id: UUID
    name: str
    damage: int = 0
    
    def __init__(self, id, name, damage) -> None:
        self.id = id
        self.name = name
        self.damage =  damage
        