from enum import Enum
import logging
from pathlib import Path

from agents.agent import Agent
from core.game import Game
from core.game_interface import GameInterface
from core.game_types import PlayerOrder
from utils.agent_factory import AgentFactory
from utils.config_manager import ConfigManager
from utils.prompt_handler import PromptHandler

logger = logging.getLogger(__name__) 


class GameResult(Enum):
    FIRST_PLAYER_WON = 0
    SECOND_PLAYER_WON = 1
    DRAW = 2
    ERROR = 3

class OneGameStats:
    def __init__(self):
        self.game_result = GameResult.ERROR 
        self.number_of_turns = 0
        self.game_path = Path("")
        self.first_agent_name = ""
        self.second_agent_name = ""

    def __str__(self):
        string_parts = []

        string_parts.append(f"Game result: {self.game_result} \n")
        string_parts.append(f"Game number_of_turns: {self.number_of_turns}\n")
        string_parts.append(f"Game game_path: {self.game_path.name}\n")
        string_parts.append(f"Game first_agent_name:\n {self.first_agent_name}\n")
        string_parts.append(f"Game second_agent_name:\n {self.second_agent_name}\n")

        return ''.join(string_parts)


# We store in one_games_stats agents names and games path so we can calculate more statistics later
class MultiGameStats:
    def __init__(self):
        self.game_stats = []

    def add_one_game_stats(self, one_game_stats: OneGameStats):
        self.game_stats.append(one_game_stats)


    def get_first_agent_wins(self) -> int:
        return sum(1 for game in self.game_stats if game.game_result == GameResult.FIRST_PLAYER_WON)

    def get_second_agent_wins(self) -> int:
        return sum(1 for game in self.game_stats if game.game_result == GameResult.SECOND_PLAYER_WON)

    def get_draws(self) -> int:
        return sum(1 for game in self.game_stats if  game.game_result == GameResult.DRAW)
    
    def get_games_with_exception(self) -> int:
        return sum(1 for game in self.game_stats if  game.game_result == GameResult.ERROR)

    def get_mean_game_length(self) -> float:
        if self.get_number_of_games() == 0:
            return 0.0
        else:
            return sum([one_game_stats.number_of_turns for one_game_stats in self.game_stats]) / self.get_number_of_games()

        
    def get_number_of_games(self):
        return len(self.game_stats)
        
    def get_stats_per_map(self):
        per_map = {}

        for game in self.game_stats:
            map_name = game.game_path

            if map_name not in per_map:
                per_map[map_name] = {
                    "games": 0,
                    "wins": 0,
                    "losses": 0,
                    "draws": 0,
                    "errors": 0,
                }

            entry = per_map[map_name]
            entry["games"] += 1

            if game.game_result == GameResult.FIRST_PLAYER_WON:
                entry["wins"] += 1
            elif game.game_result == GameResult.SECOND_PLAYER_WON:
                entry["losses"] += 1
            elif game.game_result == GameResult.DRAW:
                entry["draws"] += 1
            elif game.game_result == GameResult.ERROR:
                entry["errors"] += 1

        sorted_maps = sorted(
            per_map.items(),
            key=lambda x: x[1]["wins"] / x[1]["games"] if x[1]["games"] > 0 else 0,
            reverse=True,
        )

        lines = []
        for map_name, stats in sorted_maps:
            win_ratio = stats["wins"] / stats["games"] * 100
            line = (
                f"{(str(map_name) + ':').ljust(120)}"
                f"G={stats['games']} "
                f"W={stats['wins']} "
                f"L={stats['losses']} "
                f"D={stats['draws']} "
                f"E={stats['errors']} "
                f"WR={win_ratio:.1f}%"
            )
            lines.append(line)

        return "\n".join(lines)


    def __str__(self):
        string_parts = []
        number_of_games = self.get_number_of_games()

        string_parts.append(f"--- Multi Game Stats ---\n")
        if self.get_number_of_games() > 0:
            string_parts.append((f"Total number of games:  {number_of_games} "))
            string_parts.append((f"Number of wins: {self.get_first_agent_wins()} ({self.get_first_agent_wins() * float(100) / number_of_games:.1f})%"))
            string_parts.append((f"Number of looses: {self.get_second_agent_wins()} ({self.get_second_agent_wins() * float(100)/ number_of_games:.1f})%"))
            string_parts.append((f"Number of draws: {self.get_draws()} ({self.get_draws() * float(100) / number_of_games:.1f})%"))
            string_parts.append((f"Number of game ended with exception: {self.get_games_with_exception()} ({self.get_games_with_exception() * float(100) / number_of_games:.1f})%"))
            string_parts.append((f"Mean game length (number of turns): {self.get_mean_game_length():.1f}"))
            string_parts.append(f"\n")
            string_parts.append(f"--Stats per map--")
            string_parts.append(self.get_stats_per_map())

        else:
            string_parts.append(f"No games played")
            string_parts.append(f"\n")

        return '\n'.join(string_parts)


class Arena:
    
    @staticmethod
    def run_one_duel(first_agent: Agent, second_agent: Agent, game_config_path: Path):
        first_agent.clear_memory()
        second_agent.clear_memory()

        logger.debug(
            f"\n\n-----------------DUEL STARTS------------------\n"
            f"FIRST AGENT:\n"
            f"{first_agent}\n"
            f"SECOND AGENT:\n"
            f"{second_agent}\n"
            f"MAP:\n"
            f"{game_config_path}\n\n"
            )

        game_stats = OneGameStats()
        my_game = Game(game_config_path, first_agent, second_agent)
        
        #try:
        my_game.start()
        # except Exception as e:
        #     # game_stats.Error is default
        #     logger.debug(f"\n---GAME ENDED WITH EXCEPTION:\n"
        #                  f"{e}\n"
        #                  )


        game_stats.first_agent_name = str(first_agent)
        game_stats.second_agent_name = str(second_agent)
        game_stats.game_path = game_config_path
        game_stats.number_of_turns = my_game.get_turn_number()

        if my_game.game_ended:
            if my_game.get_is_draw():
                game_stats.game_result = GameResult.DRAW
            elif my_game.is_first_player_winner:
                game_stats.game_result = GameResult.FIRST_PLAYER_WON
            else:
                game_stats.game_result = GameResult.SECOND_PLAYER_WON

        logger.debug(
            f"\n\n-----------------DUEL ENDS------------------\n"
            f"ONE GAMES STATS:\n"
            f"{game_stats}\n\n"
                     )


        return game_stats




    def run_two_way_duel(self, first_agent, second_agent, game_path, multiple_game_stats = None):
        if multiple_game_stats is None:
            multiple_game_stats = MultiGameStats()

        # first game
        first_game_stats = self.run_one_duel(first_agent, second_agent, game_path)
        multiple_game_stats.add_one_game_stats(first_game_stats)

        # reversed game
        reversed_winning_state = self.run_one_duel(second_agent, first_agent, game_path)
        [reversed_winning_state.first_agent_name, reversed_winning_state.second_agent_name] = [reversed_winning_state.second_agent_name, reversed_winning_state.first_agent_name]
        
        if reversed_winning_state.game_result == GameResult.FIRST_PLAYER_WON:
            reversed_winning_state.game_result = GameResult.SECOND_PLAYER_WON
        elif reversed_winning_state.game_result == GameResult.SECOND_PLAYER_WON:
            reversed_winning_state.game_result = GameResult.FIRST_PLAYER_WON
        
        multiple_game_stats.add_one_game_stats(reversed_winning_state)

        return multiple_game_stats


    def run_duel_on_many_maps(self, first_agent, second_agent, game_paths, number_of_games_per_map, multiple_game_stats = None, is_two_way = True):
        if multiple_game_stats is None:
            multiple_game_stats = MultiGameStats()
        
        for game_path in game_paths:
            for i in range(number_of_games_per_map):
                if is_two_way:
                    self.run_two_way_duel(first_agent, second_agent, game_path, multiple_game_stats)
                else:
                    one_game_state = self.run_one_duel(first_agent, second_agent, game_path)
                    multiple_game_stats.add_one_game_stats(one_game_state)

        return multiple_game_stats


    def run_many_agents_against_one(self, agents, second_agent, game_paths, number_of_games_per_map):
        
        for i, first_agent in enumerate(agents):
            logger.debug(
                f"\n---AGENT NR {i + 1} STARTS ---\n"
                f"AGENT NAME\n"
                f"{first_agent}\n\n"
                )

            multiple_game_stats = self.run_duel_on_many_maps(first_agent, second_agent, game_paths, number_of_games_per_map)

            logger.debug(
                f"\n---AGENT NR {i + 1} ENDS ---\n"
                f"AGENT NAME:\n"
                f"{first_agent}\n"
                f"\n---MULTI GAME STATS---\n"
                f"{multiple_game_stats}\n\n"
                         )

    @staticmethod
    def launch_solo_game_from_config(solo_game_settings):
        first_agent = AgentFactory.create_agent(solo_game_settings['agents']['first_agent'])
        second_agent = AgentFactory.create_agent(solo_game_settings['agents']['second_agent'])
        one_game_state = Arena.run_one_duel(first_agent, second_agent, Path(solo_game_settings["game_config_path"]))
        logger.debug(
            f"\n---SOLO GAME STATS---\n"
            f"{one_game_state}\n\n"
                     )

    @staticmethod
    def launch_multiple_agents_from_config(arena_settings):
        agents_permutations = AgentFactory.generate_many_llm_agents(arena_settings['mulitiple_agents_settings'])
        second_agent = AgentFactory.create_agent(arena_settings['second_agent'])
        game_paths = ConfigManager.get_map_paths(ConfigManager.get_project_dir() / arena_settings["game_path_directory"])
        number_of_games_per_map = arena_settings["number_of_games_per_map"]
        
        arena = Arena()
        arena.run_many_agents_against_one(agents_permutations, second_agent, game_paths, number_of_games_per_map)
