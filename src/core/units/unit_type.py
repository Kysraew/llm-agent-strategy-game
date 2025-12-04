

from typing import List

from core.action import ActionType


class UnitType:
    
    def __init__(
            self,
            name: str,
            unit_symbol: str,
            max_health: int,
            attack: int,
            speed: int,
            attack_range: int,
            possible_actions: List[ActionType]
            ):

        self.name = name
        self.unit_symbol = unit_symbol
        self.max_health = max_health
        self.attack = attack
        self.speed = speed
        self.attack_range = attack_range
        self.possible_actions = possible_actions