from core.game_events.game_event import GameEvent
from core.invalid_rule import InvalidRule, InvalidActionType


class InvalidActionEvent(GameEvent):
  
  def __init__(self, current_turn, current_stage, current_try, invalid_rules: list[InvalidRule]):
    self.current_turn = current_turn
    self.current_stage = current_stage
    self.current_try = current_try
    self.invalid_rules = invalid_rules
  
  def get_description(self) -> str:
    return f"Action {self.invalid_rules[0].action} during turn:{self.current_turn} stage:{self.current_stage} try:{self.current_try} was invalid because {self.invalid_rules[0].invalid_action_type.value}."
