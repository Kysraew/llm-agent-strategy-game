from abc import ABC, abstractmethod

class GameEvent(ABC):
  
  @abstractmethod
  def __init__(self):
    pass
  
  @abstractmethod
  def get_description(self) -> str:
    pass
