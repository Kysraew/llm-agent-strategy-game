from core.position import Position
from .unit import Unit
from core.action import ActionType
from core.game_types import PlayerOrder  

class Warrior(Unit):
    HEALTH = 10
    ATTACK = 3
    SPEED = 2
    ATTACK_RANGE = 1
    UNIT_SYMBOL = 'W'
    POSSIBLE_ACTION_TYPES = [ActionType.MOVE, ActionType.ATTACK]

    def __init__(self, id: int, player_order: PlayerOrder, position: Position):
        super().__init__(
            id=id,
            player_order=player_order,
            position=position,
            health=self.HEALTH,
            attack=self.ATTACK,
            speed=self.SPEED,
            attack_range=self.ATTACK_RANGE,
            unit_symbol=self.UNIT_SYMBOL
        )
        