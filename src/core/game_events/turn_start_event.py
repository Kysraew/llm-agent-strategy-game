
from core.game_events.game_event import GameEvent


class TurnStartEvent(GameEvent):
  
  def __init__(self, turn_ended_number, player_order_of_starting_agent):
    self.turn_ended_number = turn_ended_number
    self.player_order_of_starting_agent = player_order_of_starting_agent
  
  def get_description(self) -> str:
    return f"Turn {self.turn_ended_number} player {self.player_order_of_starting_agent} starts."
