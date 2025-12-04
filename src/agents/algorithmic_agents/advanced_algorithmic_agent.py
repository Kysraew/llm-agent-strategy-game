import math
import random

from agents.agent import Agent
from core.game import Game
from core.action import Action, ActionType
from core.game_interface import GameInterface
from core.game_types import GameType
from core.position import Position

class AdvancedAlgorithmicAgent(Agent):

  def __init__(self):
    super().__init__()
    
  def choose_action(self, gameInterface: GameInterface) -> Action:
    all_possible_actions = gameInterface.get_all_possible_actions()
    agent_units = gameInterface.get_current_player_units()
    enemy_units = gameInterface.get_enemy_units()

    # Tries to attack any enemy
    attact_actions = []
    for action in all_possible_actions:
      if action.action_type == ActionType.ATTACK:
        attact_actions.append(action)

    if len(attact_actions) != 0:
      return attact_actions[0]

    # Tries to move king to safety if king isn't the unit.
    if gameInterface.get_game_type() == GameType.KILL_THE_KING and \
    len(agent_units) > 1:
      game_king_unit = gameInterface.get_king_unit_type()
      agent_king = None
      for agent_unit in agent_units:
        if agent_unit.unit_type == game_king_unit:
          agent_king = agent_unit

      if agent_king and \
      ActionType.MOVE not in agent_king.used_actions:

        king_possible_moves = gameInterface.get_unit_possible_moves(agent_king)
        king_possible_MOVE_moves = [unit_possible_move for unit_possible_move in king_possible_moves if unit_possible_move.action_type == ActionType.MOVE]          
        
        safest_king_move, _ = self._get_greatest_distance_action_to_closest_enemy(king_possible_MOVE_moves, enemy_units, gameInterface)

        return safest_king_move
        
  # Tries to MOVE units close to enemy if unit didn't attact
    for agent_unit in agent_units:

      if ActionType.MOVE not in agent_unit.used_actions and \
      ActionType.ATTACK not in agent_unit.used_actions:
        
        unit_possible_moves = gameInterface.get_unit_possible_moves(agent_unit)
        unit_possible_MOVE_moves = [unit_possible_move for unit_possible_move in unit_possible_moves if unit_possible_move.action_type == ActionType.MOVE]          
        if len(unit_possible_MOVE_moves) > 0:
          smallest_distance_action, _ =  self._get_smallest_distance_action_to_closest_enemy(unit_possible_MOVE_moves, enemy_units, gameInterface)
          return smallest_distance_action
        
        # for unit_possible_MOVE_move in unit_possible_MOVE_moves:
        #   for enemy_unit in enemy_units:
        #     if enemy_unit.position in Position.distance_area(agent_unit.position, agent_unit.unit_type.attack_range):
        #       return unit_possible_MOVE_move
              
              
    #Check if unit is in move + attack range from any enemy #TODO

    # When nothing is available
    return Action(None, None, ActionType.END_TURN)


  def _get_greatest_distance_action_to_closest_enemy(self, possible_moves, enemy_units, gameInterface: GameInterface):
    best_distance_to_enemy = 0
    action_index = 0

    for i, action in enumerate(possible_moves):
      distance_to_enemy = min(
      gameInterface.distance_with_obstacles(action.destination, e.position)
      for e in enemy_units
      )
      if distance_to_enemy > best_distance_to_enemy:
        best_distance_to_enemy = distance_to_enemy
        action_index = i

    return [ possible_moves[action_index], best_distance_to_enemy ]

  def _get_smallest_distance_action_to_closest_enemy(self, possible_moves, enemy_units, gameInterface: GameInterface):
    best_distance_to_enemy = math.inf
    action_index = 0

    for i, action in enumerate(possible_moves):
      distance_to_enemy = min(
      gameInterface.distance_with_obstacles(action.destination, e.position)
      for e in enemy_units
      )
      if distance_to_enemy < best_distance_to_enemy:
        best_distance_to_enemy = distance_to_enemy
        action_index = i

    return [ possible_moves[action_index], best_distance_to_enemy ]


  def __str__(self):
    return f"AdvancedAlgorithmicAgent"