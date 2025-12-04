from __future__ import annotations

class Position:
  x: int
  y: int
  
  def __init__(self, x: int, y: int):
      self.x = x
      self.y = y
      
  def __eq__(self, other: Position):
    return self.x == other.x and self.y == other.y
  
  @staticmethod
  def distance(first, second: Position):
    return abs(first.x - second.x) + abs(first.y - second.y) 

  @staticmethod
  def distance_area(center: Position, max_dist: int) -> list[Position]:
    positions = []
    cx, cy = center.x, center.y
    for y in range(cy - max_dist, cy + max_dist + 1):
      for x in range(cx - max_dist, cx + max_dist + 1):
        if abs(cx - x) + abs(cy - y) <= max_dist:
          positions.append(Position(x, y))
    return positions