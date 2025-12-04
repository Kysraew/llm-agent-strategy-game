
from core.game_interface import GameInterface


def empty_history(previous_history: list[str], game: GameInterface, arg_dict: dict) -> str:
    return ""

# This function edits prompt_handler previous_history state and returns history string for prompt
def basic_game_events_history(previous_history, game: GameInterface, arg_dict: dict) -> str:
    string_parts = []

    string_parts.append("Game history")
    for previous_history_entry in previous_history[-15:]:
        string_parts.append(previous_history_entry)

    # We can add some info about current game state if we want

    return '\n'.join(string_parts)

History_functions_map = {
    "empty_history": empty_history,
    "basic_game_events_history": basic_game_events_history,
}