from agents import Agent
from core.game import Game
from core.action import Action, ActionType
from core.position import Position
from core.game_interface import GameInterface

class HumanAgent(Agent):
  
  def __init__(self):
    super().__init__()
    
  
  def choose_action(self, gameInterface: GameInterface):
    
    while True: 
      print("--------------------------------")
      print(f"Player id: {gameInterface.get_current_player().value}")
      print(f"Turn number: {gameInterface.get_turn_number()}")
      
      print("Map: ")
      print(gameInterface.get_map_string())
      print("\nUnits:")
      print(gameInterface.get_units_description())


      print("\nAction type:")
      print("1. MOVE")
      print("2. ATTACK")
      print("3. END TURN")

      while True:            
        try:
          action_type_number = int(input("Write action type number:"))
          action_type = None
          match action_type_number:
            case 1:
              action_type = ActionType.MOVE
            case 2:
              action_type = ActionType.ATTACK
            case 3:
              return Action(None, None, ActionType.END_TURN) # special case
            case _:
              raise Exception("Wrong number")
          break
        except ValueError:
          print("Wrong action type format")

      while True:
        print("Source position:")
        source_x = input("Write x:")
        source_y = input("Write y:")
        try:
          source_position = Position(int(source_x), int(source_y))
          break
        except ValueError:
          print("Wrong position format")
      
      while True:            
        print("Destination position:")
        destination_x = input("Write x:")
        destination_y = input("Write y:")
        try:
          destination_position = Position(int(destination_x), int(destination_y))
          break
        except ValueError:
          print("Wrong position format")
        
      action = Action(source_position, destination_position, action_type)
      
      invalid_rules = gameInterface.is_move_vaild(action)
      if len(invalid_rules) == 0:
        return action
      else:
        print("Action is invalid. Choose another action")
    
  def __str__(self):
    return "HumanAgent"