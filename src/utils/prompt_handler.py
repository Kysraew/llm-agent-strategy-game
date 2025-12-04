from enum import Enum
from typing import Dict, List
import yaml
from jinja2 import Template 
from pathlib import Path

from core.game_events.game_event import GameEvent
from core.game_interface import GameInterface

from .config_manager import ConfigManager
from core.game import Game
from .prompt_functions.map_functions import Map_functions_map
from .prompt_functions.units_functions import Units_functions_map
from .prompt_functions.history_functions import History_functions_map
from .prompt_functions.invalid_move_functions import Invalid_functions_map


#All prompts are written in jinja2 format
class PromptHandler:
    # We have to load paths from configManager first
    _prompt_loaded = False
    prompt_type_paths: Dict[str, Path] = {}

    def __init__(self) -> None:
        PromptHandler._ensure_loaded_paths()        

        self.prompt_history: list[str] = []
        self.prompt_parts: List[dict[str, str]] = []
        self.last_invalid_rules = [] # We record why last move was invalid

    @staticmethod
    def _ensure_loaded_paths() -> None:
        if not PromptHandler._prompt_loaded:
            PromptHandler._set_prompt_files_paths()
            PromptHandler._prompt_loaded = True

    @staticmethod
    def _set_prompt_files_paths() -> None: 
        prompt_config_dict = ConfigManager.get('prompts_settings')
        for prompt_setting in prompt_config_dict:
            PromptHandler.prompt_type_paths[prompt_setting["name"]] = prompt_setting["path"]


    # Loads one prompt string from one file 
    @staticmethod
    def get_prompt_template(prompt_type: str, prompt_name: str) -> str:
        PromptHandler._ensure_loaded_paths()        

        with open(PromptHandler.prompt_type_paths[prompt_type], "r", encoding="utf-8") as f:
            return yaml.safe_load(f)[prompt_name]

    # Saves one given prompt_part in prompt_parts list 
    def add_prompt(self, prompt_part: dict[str, str]) -> None:
        self.prompt_parts.append(prompt_part)


    # Returns full render prompt based on prompt_types_order list order
    # All parameters required to render templates has to be given
    def get_full_prompt(self, game: GameInterface) -> str:
        prompt_parts = []

        for prompt_part_dict in self.prompt_parts:
            match (prompt_part_dict["type"]):
                case "MAP_FUNCTION":
                    prompt_parts.append(Map_functions_map[prompt_part_dict["name"]["name"]](game, prompt_part_dict["name"]["arguments"]))
                case "UNITS_FUNCTION":
                    prompt_parts.append(Units_functions_map[prompt_part_dict["name"]["name"]](game, prompt_part_dict["name"]["arguments"]))
                case "HISTORY_FUNCTION":
                    prompt_parts.append(History_functions_map[prompt_part_dict["name"]["name"]](self.prompt_history, game, prompt_part_dict["name"]["arguments"]))
                case "INVALID_MOVE_FUNCTION":
                    prompt_parts.append(Invalid_functions_map[prompt_part_dict["name"]](game = game, arg_dict = prompt_part_dict["arguments"]))

                case _:
                    prompt_part = self.get_prompt_template(prompt_part_dict["type"], prompt_part_dict["name"])
                    completed_part = Template(prompt_part).render(game = game)
                    prompt_parts.append(completed_part)

        return '\n'.join(prompt_parts)
    
    def get_prompt_history(self) -> str:
        return "\n".join(self.prompt_history)
    
    def clear_history(self):
        self.prompt_history = []

    def __str__(self):
        string_parts = []
        string_parts.append("   --Prompt handler--")
        for prompt_part in self.prompt_parts:
            string_parts.append(f'      {prompt_part["type"]}: {prompt_part["name"]} ')

        return "\n".join(string_parts).rstrip()
    

    def add_to_prompt_history(self, game_event: GameEvent):
        self.prompt_history.append(game_event.get_description())


    def set_prompt_at(self, index, prompt_part_dict: dict):
        self.prompt_parts[index] = prompt_part_dict