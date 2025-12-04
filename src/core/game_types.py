from enum import Enum


class Terrain(str, Enum):
  PLAINS = "."
  MOUNTAINS = "M"

class GameType(str, Enum):
  ELIMINATION = "elimination"
  KILL_THE_KING = "killTheKing"

class PlayerOrder(Enum):
  FIRST_PLAYER = 'FIRST_PLAYER '
  SECOND_PLAYER = 'SECOND_PLAYER'