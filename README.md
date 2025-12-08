# Sim World


## Start-up

Project was build on python 3.10 but should work on higher versions

1. Download project from github
2. Create new virutal environment
3. Activate new environment
4. Go to project directory and install all depencencies with pip -r "requirements.txt"
5. Go to src directory
6. Run python main.py


## Config
Main config is stored in src/config.yaml.
This config is responsibile for running games. Default main.py and config.yaml are set to use arena_settings and be able to generate and run multiple agents.
In config we can register new prompt types in prompts_settings by adding new element to the list containing name and path.

We create llm agents by listing all promp types and prompt names.
We can aloso add to prompt prompt functions:
- HISTORY_FUNCTION - history function is unique because it adds specific specific string to prompt history that is stored in prompt handler. It changes state so it should only be called during llm agent action handling
- MAP_FUNCTION
- UNIT_FUNCTION


### Logger
Python package logging is used for logging info. Logger settings are in main.py


### Game Config 
Each game config contains all necessery informations about the game. It contains units definitions, game map, game state, game mode
For now only 2 action types are implemented.

There are currently two types of terrain:
  - PLAINS = "." - these are normal fields
  - MOUNTAINS = "M" - units can't sand on them

There is only one game mode:
 - elimination - all enemy units have to be defeated
 - killTheKing - enemy king has to be defeted

## Game

This class is responsibile for running one game instance between two agents. Agents control their units by passing source position, destination position and action type. In one turn agent can use every action of every unit. Each action is one stage. In one stage agent can try specify times to return valid action, if it failes to do so, his turn ends. Game passes information to agents about successful and unsuccesfuls moves.


## Agents

This class is responsibile for choosing action for agent. Every new agents have to implement two functions: __init__ and choose_action that returns action type

### Algorithmic agents
- RandomAgent - returns random action from all available actions
- AttackFirstAgent - returns first attack action from all available actions type
- AdvancedAlgorithmicAgent - returns attack actions, if there are not, returns actions that minimalise distance to enemy

### Llm agents
 - BasicLlmAgent - it is only llm agent in this project, but it is highly configuratable because of llm_provider and prompt_handler classes. We can also use feedback from the game by passing proper history function in the agent config. 


## Additional Info