import re
import logging
from ollama import chat

from agents.agent import Agent
from core.game import Game
from core.invalid_rule import InvalidRule, InvalidActionType
from core.action import Action, ActionType
from core.game_interface import GameInterface
from llm_providers.abstract_llm_provider import AbstractLlmProvider
from core.position import Position
from core.units import *
from utils.prompt_handler import PromptHandler

logger = logging.getLogger(__name__)

class BasicLlmAgent(Agent):
 
  def __init__(self, llm_provider: AbstractLlmProvider, prompt_handler: PromptHandler):
    super().__init__()
    self.llm_provider: AbstractLlmProvider  = llm_provider    
    self.prompt_handler: PromptHandler  = prompt_handler    


  
  def choose_action(self, gameInterface: GameInterface) -> Action:

    logger.debug(f"---Llm turn: {gameInterface.get_turn_number() } stage: {gameInterface.get_turn_stage()}  try: {gameInterface.get_try_number()} response start--- ")
    # logger.debug('\n' + gameInterface.get_map_string()) # Now it is printed in game class
    # logger.debug(gameInterface.get_units_description())


    prompt = self.prompt_handler.get_full_prompt(gameInterface)
    llm_action_response = self.llm_provider.ask_llm(prompt)

    logger.debug(f"\n\nLlm prompt: {prompt}\n\n")

    logger.debug(f"\n\nLLM RESPONSE: {llm_action_response}")

    pattern = re.compile(
        r'\s*ACTION:\s*([A-Za-z_]+)\s+SOURCE:\s*\(\s*(\d+)\s*,?\s*(\d+)\s*\)\s*,?\s*TARGET:\s*\(\s*(\d+)\s*,?\s*(\d+)\s*\)\s*'
    )
    match = pattern.search(llm_action_response)
    
    agent_action = Action(None, None, None)
    try:
      agent_action = Action(
        Position(int(match.group(2)), int(match.group(3))),
        Position(int(match.group(4)), int(match.group(5))),
        ActionType[match.group(1).upper()]
        )
    except: 
      logger.debug(f"LLM response format invalid in.")
      
    logger.debug(f"---Llm turn: {gameInterface.get_turn_number() } stage: {gameInterface.get_turn_stage()} try: {gameInterface.get_try_number()} response  end--- \n\n")
    logger.debug(f"Llm parsed action: {agent_action}")

    return agent_action
  

  def notify_game_event(self, game_event):
    self.prompt_handler.add_to_prompt_history(game_event)

  def __str__(self):
      string_parts = []

      string_parts.append(f"\n")
      string_parts.append(f"|-----BasicLlmAgent-----|")
      string_parts.append(f"{self.prompt_handler}")
      string_parts.append(f"{self.llm_provider}")
      string_parts.append(f"\n")
      
      return '\n'.join(string_parts)