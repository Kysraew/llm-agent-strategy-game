from enum import Enum


class InvalidActionType(Enum):
  SOURCE_UNIT_DOES_NOT_EXIST = "SOURCE_UNIT_DOES_NOT_EXIST"
  DESTINATION_UNIT_DOES_NOT_EXIST = "DESTINATION_UNIT_DOES_NOT_EXIST"
  DESTINATION_DOES_NOT_EXISTS = "DESTINATION_DOES_NOT_EXISTS"
  TARGET_IS_CONTROLED_BY_THE_SAME_AGENT = "TARGET_IS_CONTROLED_BY_THE_SAME_AGENT"
  WRONG_TERRAIN = "WRONG_TERRAIN"
  DESTINATION_IS_OCCUPIED = "DESTINATION_IS_OCCUPIED"
  UNIT_CONTROLED_BY_ENEMY = "unit is controled by enemy"
  UNIT_CAN_NOT_BE_REACHED = "UNIT_CAN_NOT_BE_REACHED"
  MOVE_DISTANCE_TOO_GRATE = "MOVE_DISTANCE_TOO_GRATE"
  UNIT_ALREADY_DID_THIS_ACTION_IN_THIS_TURN = "UNIT_ALREADY_DID_THIS_ACTION_IN_THIS_TURN"
  DISTANCE_IS_TOO_GREAT = "DISTANCE_IS_TOO_GREAT"
  ACTION_IS_EMPTY = "ACTION_IS_EMPTY"

class InvalidRule:
  def __init__(self, invalid_action_type, action):
    self.action = action
    self.invalid_action_type = invalid_action_type

  def __str__(self):
    string_parts = []

    string_parts.append(f"Invalid Rule: {self.invalid_action_type.value} in action: {self.action}")

    return '\n'.join(string_parts)