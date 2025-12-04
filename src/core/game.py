from collections import deque
import math
import yaml
import copy
import logging
from pathlib import Path

from agents import Agent
from core.units.unit_type import UnitType
from .units import Unit
from .position import Position 
from .action import Action, ActionType
from .game_types import PlayerOrder, GameType, Terrain
from .game_interface import GameInterface
from .exceptions import GameError, InvalidMoveError, ActionAlreadyTakenError
from .invalid_rule import InvalidActionType, InvalidRule

from .game_events.game_event import GameEvent
from .game_events.invalid_action_event import InvalidActionEvent
from .game_events.succesful_move_event import SuccesfulMoveEvent
from .game_events.turn_start_event import TurnStartEvent


logger = logging.getLogger(__name__)


class Game(GameInterface):
  
  map_terrain: list[list[Terrain]]
  game_type: GameType
  first_agent: Agent
  second_agent: Agent
  player_order: PlayerOrder
  is_draw: bool
  game_ended: bool
  is_first_player_winner: bool
  turn_number: int
  units: list[Unit]
  
  
  def __init__(self, game_config_path: Path, first_agent: Agent, second_agent: Agent):
        
    self.map_terrain = [] 
    self.unit_types = {} 
    self.units = [] 
    self.first_agent = first_agent    
    self.second_agent = second_agent
    self.current_player = PlayerOrder.FIRST_PLAYER
    self.is_draw = False
    self.game_ended = False
    self.is_first_player_winner = False
    self.game_type = None
    self.king_unit_type = None
    
    self.turn_number = 1
    self.max_turn_number = None
    self.turn_stage = 1 #Each agent action is one turn_stage 
    self.try_number = 1 #Tells how many invalid actions agent passed in a row 
    
    self.load_game_from_config(game_config_path)
  

  #Loading game methods
  def load_map_terrain(self, map_settings: dict) -> None:
    terrain_lines = map_settings.strip().split('\n')
    for line in terrain_lines:
        row = []
        cells = line.split()
        for cell in cells:
          match (cell):
            case Terrain.MOUNTAINS.value:
              row.append(Terrain.MOUNTAINS)
            case Terrain.PLAINS.value:
              row.append(Terrain.PLAINS)
            case _:
              raise Exception(f"Wrong map_terrain symbol: {cell}")

        self.map_terrain.append(row)


  def load_map_units(self, unit_map: dict) -> None:
    unit_lines = unit_map.strip().split('\n')
    unit_last_id = 0
    
    for i, line in enumerate(unit_lines):
        cells = line.split()  
        for j, cell in enumerate(cells):
            if cell == '.':
                continue
                
            if len(cell) >= 2:
                unit_type_instance = self.unit_types[cell[0]]
                
                unit_owner = cell[1]
                unit_last_id += 1
                    
                if unit_owner == "1": 
                    self.units.append(Unit(unit_last_id, PlayerOrder.FIRST_PLAYER, Position(j, i), unit_type_instance))
                elif unit_owner == "2": 
                    self.units.append(Unit(unit_last_id, PlayerOrder.SECOND_PLAYER, Position(j, i), unit_type_instance))
                else:
                    raise Exception("Unit have to be controlled by either first or second agent")    


  def load_unit_types(self, unit_types_settings: dict) -> None:
    for unit_type_setting in unit_types_settings:
      unit_type_instance = UnitType(
        unit_type_setting['name'],
        unit_type_setting['unit_symbol'],
        unit_type_setting['health'],
        unit_type_setting['attack'],
        unit_type_setting['speed'],
        unit_type_setting['attack_range'],
        [ActionType[action] for action in unit_type_setting['possible_actions']]
      )

      self.unit_types[unit_type_setting['unit_symbol']] = unit_type_instance

  def load_current_state(self, game_state_settings: dict) -> None:
    self.current_player = PlayerOrder[game_state_settings['player_turn']]
    self.turn_number = game_state_settings['turn']
    
    for unit_state in game_state_settings['units']:
      unit = self.get_unit(Position(unit_state['position'][0], unit_state['position'][1]))
      unit.health = unit_state['health']

      carried_actions = unit_state.get('carried_actions')
      if carried_actions:
        for carried_action in carried_actions:
          unit.used_actions.append(ActionType[carried_action])


  def load_game_from_config(self, game_config_path: Path):
    with open(game_config_path) as f:
        config_dict = yaml.safe_load(f)
  
    self.load_map_terrain(config_dict['map_terrain'])
    self.load_unit_types(config_dict['unit_types'])
    self.load_map_units(config_dict['map_units'])

    self.max_turn_number = config_dict["max_turn_number"]
    self.max_unsuccessful_actions_tries = config_dict["max_unsuccessful_actions_tries"]

    if current_state_config := config_dict.get('game_state'): 
      self.load_current_state(current_state_config)

    game_type_name = config_dict["game_type"]
    for game_type in GameType:
      if game_type.value == game_type_name:
        self.game_type = game_type
    
    if game_type is None:
      raise Exception("Wrong game type")
    elif game_type == GameType.KILL_THE_KING:
      king_unit_symbol = config_dict.get('king_unit_symbol')
      self.king_unit_type = self.unit_types.get(king_unit_symbol)
      if self.king_unit_type is None:
        raise Exception("killTheKing has to have defined king unit")


  def notify_agents(self, game_event: GameEvent):
    self.first_agent.notify_game_event(game_event)
    self.second_agent.notify_game_event(game_event)


  def start(self):
    while not self.game_ended:        
        self.process_player_turn()
        
        if self.game_ended:
          break
        
        if self.current_player == PlayerOrder.FIRST_PLAYER:
          self.current_player = PlayerOrder.SECOND_PLAYER
        else:
          self.current_player = PlayerOrder.FIRST_PLAYER
          self.turn_number += 1

        if self.turn_number >= self.max_turn_number:
          self.is_draw = True
          self.game_ended = True
          break

    if self.is_draw:
      logger.info("Game ended: Draw")
    else:
      winner_id = 1 if self.is_first_player_winner else 2
      logger.info(
        f"Game ended: Player {winner_id} won"
        )    

  def process_player_turn(self):
    if self.current_player == PlayerOrder.FIRST_PLAYER:
      active_agent = self.first_agent
    else:
      active_agent = self.second_agent
     
    self.notify_agents(TurnStartEvent(self.turn_number, self.current_player))    
    
    ending_move = False
    self.turn_stage = 1
    self.try_number = 1  
    
    while ending_move is False and self.try_number <= self.max_unsuccessful_actions_tries:
        logger.info(f"\n{self.get_map_string()}")
        logger.info(f"\n{self.get_units_description()}")
        
        agent_action = active_agent.choose_action(self)
        invalid_rules = self.is_move_vaild(agent_action)

        if len(invalid_rules) == 0:
            ending_move = self.make_move(agent_action)
            
            self.notify_agents(SuccesfulMoveEvent(self.turn_number, self.turn_stage, self.try_number, agent_action))    
            
            self.try_number = 1
            self.turn_stage += 1
        else:
            self.notify_agents(InvalidActionEvent(self.turn_number, self.turn_stage, self.try_number, invalid_rules))    
            logger.debug(f"Agent {self.current_player.value} tried making invalid action: {agent_action}.\n{invalid_rules[0]}")

            self.try_number += 1 

    if len(invalid_rules) > 0: # So we had to leave the loop because too many unsuccesful attempts occured
      logging.debug(f"Agent {self.get_current_player_id()} made too many mistakes. Turn ends automaticly")

    for unit in self.units: 
      unit.used_actions = []


  def make_move(self, action: Action):
    logger.info(f"Agent {self.current_player.value} made action: {action}")

    if action.action_type != ActionType.END_TURN:
      active_unit = self.get_unit(action.source)
    
    ending_move = False
    
    match action.action_type:
      case ActionType.END_TURN:
        ending_move = True
      case ActionType.MOVE:
        active_unit.position = action.destination
      case ActionType.ATTACK:
        target_unit = self.get_unit(action.destination)
        target_unit.health -= active_unit.unit_type.attack        
        logging.info(f"Agent {self.get_current_player_id()}. Unit {self.get_short_unit_string(active_unit)}attacked {self.get_short_unit_string(target_unit)}")

        if target_unit.health <= 0:
          logging.info(f"Unit {self.get_short_unit_string(target_unit)}was killed")
          
          self.units = [u for u in self.units if u.health > 0]
          game_ended = None
          # Checking end GameCondition
          match self.game_type:
            case GameType.ELIMINATION:
                game_ended = self.is_elimination_end_game_condition_satisfied()
            case GameType.KILL_THE_KING:
              game_ended = self.is_kill_the_king_end_game_condition_satisfied()
            case _:
              Exception("Unknown game type") 
          
          if game_ended:
            ending_move = True
            self.game_ended = True
            self.is_draw = False
            self.is_first_player_winner = self.current_player == PlayerOrder.FIRST_PLAYER  
            
    if not ending_move:
      active_unit.used_actions.append(action.action_type)
      
    return ending_move
  
  def is_elimination_end_game_condition_satisfied(self) -> bool:
    if len(self.get_player_units(self.get_opponent_player())) == 0:
      return True
    else:
      return False

  def opponent_has_unit_type(self, unit_type: UnitType) -> bool:
      opp = self.get_opponent_player()
      return any(
          u.unit_type == unit_type and u.player_order == opp
          for u in self.units
      )

  def is_kill_the_king_end_game_condition_satisfied(self) -> bool:
    return not self.opponent_has_unit_type(self.king_unit_type)
    
  def is_on_map(self, position: Position):
    if position.x >= 0 \
    and position.y >= 0 \
    and position.x < self.get_map_width() \
    and position.y < self.get_map_height():
      return True
    
    return False


# Method retuns list with invalid rules
  def is_move_vaild(self, action: Action) -> list:
    
    invalid_rules = []

    if action.action_type == ActionType.END_TURN:
      return invalid_rules
    
    if action.action_type is None:
      invalid_rules.append(InvalidRule(InvalidActionType.ACTION_IS_EMPTY, action))
      return invalid_rules

    active_unit = self.get_unit(action.source)

    if active_unit is None:
      invalid_rules.append(InvalidRule(InvalidActionType.SOURCE_UNIT_DOES_NOT_EXIST, action))
      return invalid_rules

    if self.current_player != active_unit.player_order:
      invalid_rules.append(InvalidRule(InvalidActionType.UNIT_CONTROLED_BY_ENEMY, action))
      return invalid_rules

    if action.action_type in active_unit.used_actions:
      invalid_rules.append(InvalidRule(InvalidActionType.UNIT_ALREADY_DID_THIS_ACTION_IN_THIS_TURN, action))
      return invalid_rules


    match action.action_type:
      case ActionType.MOVE:
        if self.get_unit(action.destination):
          invalid_rules.append(InvalidRule(InvalidActionType.DESTINATION_IS_OCCUPIED, action))
          return invalid_rules
        
        if action.destination not in self.get_reachable_positions(action.source, active_unit.unit_type.speed):
          invalid_rules.append(InvalidRule(InvalidActionType.DISTANCE_IS_TOO_GREAT, action))
          return invalid_rules
          
        if not self.is_on_map(action.destination):
          invalid_rules.append(InvalidRule(InvalidActionType.DESTINATION_DOES_NOT_EXISTS, action))
          return invalid_rules
          
        if self.map_terrain[action.destination.y][action.destination.x] == Terrain.MOUNTAINS:
          invalid_rules.append(InvalidRule(InvalidActionType.WRONG_TERRAIN, action))
          return invalid_rules
        

        
        return invalid_rules


      case ActionType.ATTACK:
        if action.destination not in self.get_possible_unrestrained_destinations(action.source, active_unit.unit_type.attack_range):
          invalid_rules.append(InvalidRule(InvalidActionType.DISTANCE_IS_TOO_GREAT, action))
          return invalid_rules

        if not self.is_on_map(action.destination):
          invalid_rules.append(InvalidRule(InvalidActionType.DESTINATION_DOES_NOT_EXISTS, action))
          return invalid_rules

        if self.get_unit(action.destination) is None:
          invalid_rules.append(InvalidRule(InvalidActionType.DESTINATION_UNIT_DOES_NOT_EXIST, action))
          return invalid_rules

        if self.get_unit(action.destination).player_order == active_unit.player_order:
          invalid_rules.append(InvalidRule(InvalidActionType.TARGET_IS_CONTROLED_BY_THE_SAME_AGENT, action))
          return invalid_rules

        return invalid_rules
      
      case _:
        raise Exception("Wrong action format")    
    
    

  
  def get_player_units(self, player_order: PlayerOrder):
    return [u for u in self.units if u.player_order == player_order]
  
  def get_unit(self, position: Position):
    
    for unit in self.units:
      if unit.position == position:
        return unit
    
    return None
  

  def get_unit_possible_moves(self, unit: Unit):
    possible_actions = []
    if not ActionType.MOVE in unit.used_actions:
            possible_destinations = self.get_reachable_positions(unit.position, unit.unit_type.speed)
            
            for possible_destination in possible_destinations:
              if self.get_unit(possible_destination) is None and \
              self.map_terrain[possible_destination.y][possible_destination.x] == Terrain.PLAINS:
                possible_actions.append(Action(copy.deepcopy(unit.position), possible_destination, ActionType.MOVE))
          
    if not ActionType.ATTACK in unit.used_actions:
      possible_target_destinations = self.get_possible_unrestrained_destinations(unit.position, unit.unit_type.attack_range)
      
      for possible_target_destination in possible_target_destinations:
        target_unit = self.get_unit(possible_target_destination)
        
        if target_unit is not None \
          and target_unit.player_order != unit.player_order:
            possible_actions.append(Action(copy.deepcopy(unit.position), possible_target_destination, ActionType.ATTACK))
          
    return possible_actions

  def get_all_possible_actions(self):
    all_possible_actions = []

    for unit in self.get_player_units(self.current_player):
      all_possible_actions.extend(self.get_unit_possible_moves(unit))

    all_possible_actions.append(Action(None, None, ActionType.END_TURN))
    return all_possible_actions

    
  # returns all positions in manhattan distance from given position, independend of terrain type and mountains in between
  def get_possible_unrestrained_destinations(self, position: Position, unit_range: int):
    unit_x = position.x
    unit_y = position.y
    positions = []

    for y in range(max(0, unit_y - unit_range), min(self.get_map_height(), unit_y + unit_range + 1)):
      left_range = unit_range - abs(unit_y - y)
      
      for x in range(max(0, unit_x - left_range), min(self.get_map_width(), unit_x + left_range + 1)):
        positions.append(Position(x, y))

    return positions 


# Pathfinding

  def _is_walkable(self, p: Position) -> bool:
      return (
          self.map_terrain[p.y][p.x] == Terrain.PLAINS
          and self.get_unit(p) is None
      )

  def _neighbors4(self, p: Position):
      for dx, dy in ((1,0), (-1,0), (0,1), (0,-1)):
          nx, ny = p.x + dx, p.y + dy
          if 0 <= nx < self.get_map_width() and 0 <= ny < self.get_map_height():
              yield Position(nx, ny)


  def distance_with_obstacles(self, start: Position, end: Position) -> int:
      if start == end:
          return 0

      q = deque([(start, 0)])
      visited = {(start.x, start.y)}

      while q:
          cur, dist = q.popleft()
          for nb in self._neighbors4(cur):
              key = (nb.x, nb.y)

              if key in visited:
                  continue

              if nb == end:
                  return dist + 1

              if not self._is_walkable(nb):
                  continue

              visited.add(key)
              q.append((nb, dist + 1))

      return math.inf

  # Takes into account units and mountains 
  def get_reachable_positions(self, position: Position, speed: int):
      start = position
      start_key = (start.x, start.y)
      q = deque([start])
      dist = {start_key: 0}
      reachable: list[Position] = []
      seen = {start_key}

      while q:
          cur = q.popleft()
          cur_key = (cur.x, cur.y)
          for nb in self._neighbors4(cur):
              nb_key = (nb.x, nb.y)
              if nb_key in seen:
                  continue
              if not self._is_walkable(nb):
                  continue
              nd = dist[cur_key] + 1
              if nd <= speed:
                  dist[nb_key] = nd
                  seen.add(nb_key)
                  q.append(nb)
                  reachable.append(nb)

      return reachable




  # Game descriptions


  def get_short_unit_string(self, unit: Unit):
    return f"{'1' if unit.player_order == PlayerOrder.FIRST_PLAYER else '2'}{unit.unit_type.unit_symbol}{unit.id:02} "

  def get_map_string(self):
    map_symbols = []
    for terrain_row in self.map_terrain:
      map_row = []
      for terrain_cell in terrain_row:
        map_row.append(f"{terrain_cell.value}    ") # 3 whitespaces, 4 chars total 
      map_symbols.append(map_row)
    
    for unit in self.units:
      map_symbols[unit.position.y][unit.position.x] = f"{self.get_short_unit_string(unit)}"
    
    map_string_lines = []
    
    map_string_lines.append("Y\\X ")
    for i in range(self.get_map_width()):
      map_string_lines.append(f"{i:02}   ")
    map_string_lines.append("\n\n")
      
    for i, symbols_row in enumerate(map_symbols):
      map_string_lines.append(f"{i:02}   ")
      map_string_lines.extend(symbols_row)
      map_string_lines.append("\n\n")
    
    return "".join(map_string_lines)

  def get_units_description(self): # in future can be repleaced with tameplate
    units_description_parts = []

    first_player_units_parts = [] 
    second_player_units_parts = []
    
    units_description_parts.append("Units descriptions:\n\n")

    for unit in self.units:
      if unit.player_order == PlayerOrder.FIRST_PLAYER:
        first_player_units_parts.append(f"{str(unit)}\n")
      else:
        second_player_units_parts.append(f"{str(unit)}\n")

    units_description_parts.append("First player units:\n")
    units_description_parts.extend(first_player_units_parts)

    units_description_parts.append("\nSecond player units:\n")
    units_description_parts.extend(second_player_units_parts)

    return "".join(units_description_parts)




     
    

  def get_map_width(self):
    return len(self.map_terrain[0])

  def get_map_height(self):
    return len(self.map_terrain)

  def get_current_player(self) -> PlayerOrder:
    return self.current_player
  
  def get_opponent_player(self)-> PlayerOrder:
    if self.current_player == PlayerOrder.FIRST_PLAYER:
        return PlayerOrder.SECOND_PLAYER
    else:
        return PlayerOrder.FIRST_PLAYER

  def get_current_player_id(self):
    return 1 if self.current_player == PlayerOrder.FIRST_PLAYER else 2
  
  def get_turn_number(self):
    return self.turn_number
  
  def get_units(self):
    return self.units

  def get_map_terrain(self):
    return self.map_terrain

  def get_turn_stage(self):
    return self.turn_stage

  def get_try_number(self):
    return self.try_number

  def get_first_player_units(self):
    return [unit for unit in self.units if unit.player_order == PlayerOrder.FIRST_PLAYER]

  def get_second_player_units(self):
    return [unit for unit in self.units if unit.player_order == PlayerOrder.SECOND_PLAYER]

  def get_winner_id(self):
      if not self.game_ended:
        return None
      return 1 if self.is_first_player_winner else 2

  def get_is_draw(self):
      return self.is_draw
  

  def get_current_player_units(self):
      if self.current_player == PlayerOrder.FIRST_PLAYER:
        return self.get_first_player_units()
      else:
        return self.get_second_player_units()


  def get_enemy_units(self):
      if self.current_player == PlayerOrder.FIRST_PLAYER:
        return self.get_second_player_units()
      else:
        return self.get_first_player_units()
      
  def get_king_unit_type(self):
      return self.king_unit_type

  def get_game_type(self):      
    return self.game_type