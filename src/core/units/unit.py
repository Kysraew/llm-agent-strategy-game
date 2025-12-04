from __future__ import annotations
from abc import ABC, abstractmethod

from core.position import Position
from core.game_types import PlayerOrder
from core.action import ActionType
from core.units.unit_type import UnitType
 
class Unit():
  
  HEALTH: int
  ATTACK: int
  SPEED: int
  ATTACK_RANGE: int
  UNIT_SYMBOL: str
  used_actions: list[ActionType]
  
  id: int
  player_order: int
  health: int
  attack: int
  attack_range: int
  speed: int
  unit_symbol: str
  position: Position
  
  def __init__(self, id: int, player_order: PlayerOrder, position: Position, unit_type: UnitType):
      self.id = id
      self.player_order = player_order
      self.position = position
      self.health = unit_type.max_health
      self.used_actions = []
      self.unit_type = unit_type


  def __str__(self):
    available_actions_names = ", ".join(action_type.name for action_type in self.unit_type.possible_actions if action_type not in self.used_actions) if self.unit_type.possible_actions else "-"

    return (f"{self.unit_type.name}(id={self.id}, player_order={self.player_order.value}, position=({self.position.x}, {self.position.y}), "
            f"health={self.health} / {self.unit_type.max_health}, attack={self.unit_type.attack}, attack range={self.unit_type.attack_range}, "
            f"speed range={self.unit_type.speed}, symbol='{self.unit_type.unit_symbol}') available actions='{available_actions_names}'")

