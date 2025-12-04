import yaml
from pathlib import Path

from agents.algorithmic_agents.random_agent import RandomAgent
from agents.special.human_agent import HumanAgent
from llm_providers.ollama_provider import OllamaProvider 


class ConfigManager:
    _config  = {}
    _config_path = None
    _project_dir = None
    _ollama_options = {}

    @staticmethod
    def load(path: str | Path):
        with open(path, "r", encoding="utf-8") as f:
            ConfigManager._config = yaml.safe_load(f)

    @staticmethod
    def load_ollama_options(path: str | Path):
        with open(path, "r", encoding="utf-8") as f:
            ConfigManager._ollama_options = yaml.safe_load(f)

    @staticmethod
    def get_ollama_options(ollama_option_name: str):
        return None
        # return ConfigManager._ollama_options.get(ollama_option_name)

    @staticmethod
    def get(key):
        return ConfigManager._config.get(key)
 
    @staticmethod
    def add_project_dir(project_dir_path):
        ConfigManager._project_dir = project_dir_path

    @staticmethod
    def get_project_dir():
        return ConfigManager._project_dir

    @staticmethod
    def get_map_paths(directory):
        base_path = ConfigManager._project_dir / directory
        if not base_path.exists():
            raise FileNotFoundError(f"Directory not found: {base_path}")
        if not base_path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {base_path}")
    
        return ConfigManager._collect_yaml_files(base_path)


    @staticmethod
    def _collect_yaml_files(path: Path):
        yaml_files = []
        for item in path.iterdir():
            if item.is_dir():
                yaml_files.extend(ConfigManager._collect_yaml_files(item))
            elif item.is_file() and item.suffix.lower() == ".yaml":
                yaml_files.append(item)
         
        return yaml_files
    
