from agents.algorithmic_agents.advanced_algorithmic_agent import AdvancedAlgorithmicAgent
from agents.algorithmic_agents.attact_first_agent import AttactFirstAgent
from agents.special.human_agent import HumanAgent
from agents.algorithmic_agents.random_agent import RandomAgent
from agents.llm_agents.basic_llm_agent import BasicLlmAgent
from llm_providers.abstract_llm_provider import AbstractLlmProvider
from llm_providers.ollama_provider import OllamaProvider
from utils.config_manager import ConfigManager
from utils.prompt_handler import PromptHandler

class AgentFactory:


    # example settings
    # prompt_handler:
    #   system_prompt_name: "basic_prompt"
    #   role_prompt_name: "basic_prompt"
    #   game_description_prompt_name: "basic_prompt"
    #   map_prompt_name: "basic_prompt"
    #   unit_prompt_name: "basic_prompt"
    #   prompt_parts_order:
    #   - SYSTEM
    #   - ROLE
    #   - GAME_DESCRIPTION
    #   - MAP
    #   - UNITS

    #Maybe we should simplify this 
    @staticmethod
    def get_prompt_handler(prompt_handler_settings: dict) -> PromptHandler:
        prompt_handler = PromptHandler()
        
        if prompt_handler_settings:
            prompt_part_dicts = prompt_handler_settings.get('prompt_parts')
            for prompt_part_dict in prompt_part_dicts:
                prompt_handler.add_prompt(prompt_part_dict)
        
        return prompt_handler
            
    @staticmethod
    def get_llm_provider(llm_provider_name, model_name, model_options_name = None) -> AbstractLlmProvider:
        if model_options_name is not None:
            model_options = ConfigManager.get_ollama_options(model_options_name)
        else:
            model_options = None

        if llm_provider_name == "OllamaProvider":
            return OllamaProvider(model_name, model_options)
        else:
            raise ValueError(f"Unknown provider type: {llm_provider_name}")
    
    @staticmethod
    def create_agent(agent_dict: dict):
        match agent_dict["type"]:
            case "HumanAgent":
                return HumanAgent()
            case "RandomAgent":
                return RandomAgent()
            case "AttackFirstAgent":
                return AttactFirstAgent()
            case "AdvancedAlgorithmicAgent":
                return AdvancedAlgorithmicAgent()
            case "BasicLlmAgent":
                provider = AgentFactory.get_llm_provider(agent_dict["llm_provider"]["type"], agent_dict["llm_provider"]["model"], agent_dict["llm_provider"].get("model_options_name"))
                handler = AgentFactory.get_prompt_handler(agent_dict['prompt_handler'])
                return BasicLlmAgent(provider, handler)
            case _:
                raise ValueError(f"Unknown agent type: {agent_dict['type']}")
            

    @staticmethod
    def generate_agents_with_diffrent_model_options(agent_dict: dict, model_options: list):
        for model_option in model_options:
            agent_dict["llm_provider"]["model_options_name"] = model_option
            yield AgentFactory.create_agent(agent_dict)

    @staticmethod
    def generate_many_llm_agents(mulitiple_agents_settings: dict):
        
        prompt_parts_list = []

        # We prepare agent dict to create new agenets
        current_agent_dict = {
            "type": mulitiple_agents_settings["type"],
            "llm_provider": mulitiple_agents_settings["llm_provider"],
            "prompt_handler": 
                {"prompt_parts": prompt_parts_list}
                
        }
        
        number_of_prompt_parts = len(mulitiple_agents_settings["prompt_parts"])
        number_of_options_per_prompt_part = [] 
        current_options_list = []  

        # We create our lists number_of_options_per_prompt_part and current_options_list  
        for prompt_type_parts in mulitiple_agents_settings["prompt_parts"]:
            number_of_options_per_prompt_part.append(len(prompt_type_parts["names"]))
            current_options_list.append(0)


        # We create first prompt_handler_config
        for i, prompt_type_parts in enumerate(mulitiple_agents_settings["prompt_parts"]):
            prompt_part_config = {
                "type": prompt_type_parts["type"],
                "name": prompt_type_parts["names"][0],
            }
            prompt_parts_list.append(prompt_part_config)


        # We iterate after every prompt permutation
        while True:
            
            if mulitiple_agents_settings.get("model_options_names"):
                for agent in AgentFactory.generate_agents_with_diffrent_model_options(current_agent_dict, mulitiple_agents_settings["model_options_names"]):
                    yield agent
            else:
                yield AgentFactory.create_agent(current_agent_dict)

            for i in range(number_of_prompt_parts): 
                if current_options_list[i] + 1 < number_of_options_per_prompt_part[i]:
                    current_options_list[i] += 1
                    prompt_parts_list[i] = {
                        "type": mulitiple_agents_settings["prompt_parts"][i]["type"],
                        "name": mulitiple_agents_settings["prompt_parts"][i]["names"][current_options_list[i]],
                    }
                    break
                else:
                    current_options_list[i] = 0
                    prompt_parts_list[i] = {
                        "type": mulitiple_agents_settings["prompt_parts"][i]["type"],
                        "name": mulitiple_agents_settings["prompt_parts"][i]["names"][current_options_list[i]],
                    }
            else:
                break