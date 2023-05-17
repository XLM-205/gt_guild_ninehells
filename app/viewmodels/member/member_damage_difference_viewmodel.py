from app.viewmodels.member.member_damage_viewmodel import MemberDamageViewModel


class MemberDamageDifferenceViewModel(MemberDamageViewModel):
    difference: int
    good_improvement = True
    
    def __init__(self, name, damage, difference, id) -> None:
        self.id = id
        self.name = name
        self.damage = damage
        self.difference = 0 if difference is None else difference
        if self.damage == 0:
            self.good_improvement = False
        elif self.difference < 0:
            self.good_improvement = False if abs(self.difference / self.damage) >= 0.05 else True
        