from abc import ABC, abstractmethod

from .action import Action

class GameInterface(ABC):
    @abstractmethod
    def get_all_possible_actions(self) -> list[Action]:
        pass
    
    @abstractmethod
    def get_map_width(self):
        pass
    
    @abstractmethod
    def get_map_height(self):
        pass
    
    @abstractmethod
    def get_current_player(self):
        pass
    
    @abstractmethod
    def get_turn_number(self):
        pass
    
    @abstractmethod
    def get_map_string(self):
        pass

    @abstractmethod
    def get_current_player_id(self):
        pass
    
    @abstractmethod
    def get_units_description(self):
        pass

    @abstractmethod
    def get_first_player_units(self):
        pass

    @abstractmethod
    def get_second_player_units(self):
        pass

    @abstractmethod
    def get_units(self):
        pass

    @abstractmethod
    def get_map_terrain(self):
        pass

    @abstractmethod
    def get_turn_stage(self):
        pass

    @abstractmethod
    def get_try_number(self):
        pass
    
    @abstractmethod
    def get_winner_id(self):
        pass

    @abstractmethod
    def get_is_draw(self):
        pass

    @abstractmethod
    def get_current_player_units(self):
        pass

    @abstractmethod
    def get_enemy_units(self):
        pass

    @abstractmethod
    def get_king_unit_type(self):
        pass

    @abstractmethod
    def get_unit_possible_moves(self, unit):
        pass

    @abstractmethod
    def get_game_type(self):
        pass
    
    @abstractmethod
    def distance_with_obstacles(self, start, end):
        pass


