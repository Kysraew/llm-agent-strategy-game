
from core.game_interface import GameInterface


def basic_invalid_move(invalid_rules: list, arg_dict: dict) -> str:
    string_parts = []

    for invalid_rule in invalid_rules:
        string_parts.append(str(invalid_rule))

    return '\n'.join(string_parts)


Invalid_functions_map = {
    "basic_invalid_move": basic_invalid_move
}