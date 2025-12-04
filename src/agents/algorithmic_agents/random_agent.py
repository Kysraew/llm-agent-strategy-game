import random

from agents.agent import Agent
from core.game import Game
from core.action import Action
from core.game_interface import GameInterface

class RandomAgent(Agent):

  def __init__(self):
    super().__init__()
    
  def choose_action(self, gameInterface: GameInterface) -> Action:
    possible_actions = gameInterface.get_all_possible_actions()
    
    return possible_actions[random.randint(0, len(possible_actions) - 1)]

  def __str__(self):
    return f"RandomAgent"