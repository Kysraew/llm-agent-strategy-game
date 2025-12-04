from abc import ABC, abstractmethod
import random

from core.game_interface import GameInterface
from core.action import Action

class Agent(ABC):
  
  @abstractmethod
  def __init__(self):
    pass
  
  @abstractmethod
  def choose_action(self, gameInterface: GameInterface) -> Action:
    pass

  def clear_memory(self):
    pass

  def add_invalid_move_info(self, invalid_rules):
    pass

  def notify_game_event(self, game_event):
    pass