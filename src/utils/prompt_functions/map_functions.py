
from core.game_interface import GameInterface
from core.game_types import PlayerOrder


def basic_map_description(game: GameInterface, arg_dict: dict):
    map_symbols = []
    for terrain_row in game.get_map_terrain():
        map_row = []
        for terrain_cell in terrain_row:
            map_row.append(f"{terrain_cell.value}    ") # 3 whitespaces, 4 chars total 
        map_symbols.append(map_row)

    for unit in game.get_units():
        map_symbols[unit.position.y][unit.position.x] = f"{'1' if unit.player_order == PlayerOrder.FIRST_PLAYER else '2'}{unit.unit_type.unit_symbol}{unit.id:02} "

    map_string_lines = []

    map_string_lines.append("Y\\X ")
    for i in range(game.get_map_width()):
        map_string_lines.append(f"{i:02}   ")
    map_string_lines.append("\n\n")
        
    for i, symbols_row in enumerate(map_symbols):
        map_string_lines.append(f"{i:02}   ")
        map_string_lines.extend(symbols_row)
        map_string_lines.append("\n\n")

    return "".join(map_string_lines)
  



Map_functions_map = {
    "basic_map_description": basic_map_description,
}