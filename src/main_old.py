from pathlib import Path
import logging
import signal
import sys
print("EXE:", sys.executable)
print("PATH[0]:", sys.path[0])

from core.arena import Arena
from core.game import Game
from utils.agent_factory import AgentFactory
from utils.config_manager import ConfigManager

def setup_logging(filename="sim_world.log"):
  logging.basicConfig(
      level=logging.DEBUG,          
      format='%(asctime)s - %(levelname)s - %(message)s',  # Format
      handlers= [
            logging.StreamHandler(),
            logging.FileHandler(filename)  # logi do pliku

      ]
  )
    
  logging.getLogger('core.game').setLevel(logging.DEBUG)

  logging.getLogger('httpx').setLevel(logging.WARNING)
  logging.getLogger('httpcore').setLevel(logging.WARNING)
  logging.getLogger('ollama').setLevel(logging.WARNING)


def main():
  # Config
  setup_logging()
  ConfigManager.add_project_dir(Path(__file__).parent.parent)
  ConfigManager.load(ConfigManager.get_project_dir() / 'config.yaml')
  ConfigManager.load_ollama_options(ConfigManager.get_project_dir() / ConfigManager.get('model_options_path'))

  # Agents
  human_agent = AgentFactory.create_agent({"type": "HumanAgent"})
  random_agent = AgentFactory.create_agent({"type": "RandomAgent"})
  attack_first_agent = AgentFactory.create_agent({"type": "AttackFirstAgent"})
  advanced_algorithmic_agent = AgentFactory.create_agent({"type": "AdvancedAlgorithmicAgent"})

  # Custom run
  # arena = Arena()
  # game_paths = ConfigManager.get_map_paths(ConfigManager.get_project_dir() / "src/game_configs/kill_the_king/")
  # multiple_game_stats = arena.run_duel_on_many_maps(advanced_algorithmic_agent, attack_first_agent , game_paths, 5)
  # print(multiple_game_stats)
  
  # # Arena game from config
  arena_game_settings = ConfigManager.get("arena_settings")
  Arena.launch_multiple_agents_from_config(arena_game_settings)
 
  # # Solo game from config
  # solo_game_settings = ConfigManager.get("solo_game_settings")
  # Arena.launch_solo_game_from_config(solo_game_settings)




if __name__ == "__main__":
  main()