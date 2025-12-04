from core.game_interface import GameInterface
from core.game_types import PlayerOrder


def basic_units_description(game: GameInterface, arg_dict: dict): # in future can be repleaced with tameplate
    units_description_parts = []

    first_player_units_parts = [] 
    second_player_units_parts = []

    units_description_parts.append("\nUnits descriptions:\n\n")

    for unit in game.units:
        if unit.player_order == PlayerOrder.FIRST_PLAYER:
            first_player_units_parts.append(f"{str(unit)}\n")
        else:
            second_player_units_parts.append(f"{str(unit)}\n")

    units_description_parts.append("First player units:\n")
    units_description_parts.extend(first_player_units_parts)

    units_description_parts.append("\nSecond player units:\n")
    units_description_parts.extend(second_player_units_parts)

    return "".join(units_description_parts)


Units_functions_map = {
    "basic_units_description": basic_units_description
}