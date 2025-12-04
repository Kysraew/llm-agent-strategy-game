from core.game_events.game_event import GameEvent
from core.invalid_rule import InvalidRule, InvalidActionType


class SuccesfulMoveEvent(GameEvent):
  
  def __init__(self, current_turn, current_stage, current_try, action):
    self.current_turn = current_turn
    self.current_stage = current_stage
    self.current_try = current_try
    self.action = action
  
  def get_description(self) -> str:
    return f"Action {self.action} during turn:{self.current_turn} stage:{self.current_stage} try:{self.current_try} was succesful"
