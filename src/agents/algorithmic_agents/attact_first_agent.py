import random

from agents.agent import Agent
from core.game import Game
from core.action import Action, ActionType
from core.game_interface import GameInterface

class AttactFirstAgent(Agent):

  def __init__(self):
    super().__init__()
    
  def choose_action(self, gameInterface: GameInterface) -> Action:
    possible_actions = gameInterface.get_all_possible_actions()
    
    first_attact_action = next((x for x in possible_actions if x.action_type == ActionType.ATTACK ), None)

    if first_attact_action:
        return first_attact_action
    else:
        return possible_actions[random.randint(0, len(possible_actions) - 1)]
    
  def __str__(self):
    return f"AttackFirstAgent"