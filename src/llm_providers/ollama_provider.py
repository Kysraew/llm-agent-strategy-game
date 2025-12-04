import re
from ollama import Client
import yaml

from llm_providers.abstract_llm_provider import AbstractLlmProvider
class OllamaProvider(AbstractLlmProvider):
    
    def __init__(self, model_name, model_options = None, host="http://localhost:11434"):
        self.client = Client(host)
        self.model_name = model_name
        self.model_options = model_options

    def strip_thinking_part(self, input, starting_part="<thinking>", ending_part="</thinking>"):
        patter = f'{starting_part}.*{ending_part}'
        return re.sub(patter, '', input, flags=re.DOTALL)

    # def ask_llm(self, prompt, delete_thinking_part=False, option_set='default'):
    #     response = self.client.generate(
    #         model=self.model_name,
    #         prompt=prompt,
    #         messages=[{"role": "user", "content": prompt}],
    #         options=self.model_options
    #     )
        
    #     if delete_thinking_part:
    #         return self.strip_thinking_part(response['message']['content'])
    #     else:
    #         return response['message']['content']
    
    def ask_llm(self, prompt, delete_thinking_part=False, option_set='default'):
        response = self.client.chat(
            model=self.model_name,
            messages=[
                # {
                #     "role": "system", 
                #     "content": "/set nothink"
                # },
                {"role": "user", "content": prompt}
            ],
            stream=False,
            # timeout=600.0,
            options=self.model_options
        )

        msg = response["message"]["content"]

        if delete_thinking_part:
            return self.strip_thinking_part(msg)
        return msg
        
    def __str__(self):
        string_parts = []

        string_parts.append(f"  --Ollama provider--")
        string_parts.append(f"| Model name: {self.model_name}")
        # string_parts.append(f" | Model options: {self.model_options}")

        return ''.join(string_parts)