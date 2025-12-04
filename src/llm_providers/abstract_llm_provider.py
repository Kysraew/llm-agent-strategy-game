from abc import ABC, abstractmethod

class AbstractLlmProvider(ABC):

    @abstractmethod
    def ask_llm(prompt: str, delete_thinking_part = False) -> None:
        pass