from enum import Enum

from .position import Position

class ActionType(Enum):
  MOVE = "MOVE",
  ATTACK = "ATTACK",
  # HEAL = "HEAL",
  END_TURN = "END_TURN",
  

class Action:
  source: Position
  destination: Position
  action_type: ActionType
  #unit_id: int

  def __init__(self, source: Position, destination: Position, action_type: ActionType):
      self.source = source
      self.destination = destination
      self.action_type = action_type

  def __str__(self):
      action_name_str = f"({self.action_type.name})" if self.action_type else "None"
      src_str = f"({self.source.x}, {self.source.y})" if self.source else "None"
      dst_str = f"({self.destination.x}, {self.destination.y})" if self.destination else "None"
      return f"Action(type={action_name_str}, source={src_str}, destination={dst_str})"
