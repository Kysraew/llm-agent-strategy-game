class GameError(Exception):
    pass

class InvalidMoveError(GameError):
    pass
  
class ActionAlreadyTakenError(InvalidMoveError):
    pass