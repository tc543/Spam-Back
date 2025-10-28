import ollama

class llama3:
    """
    Meta llama3 model

    Args:
        model (str): Can only accept these models
        - llama3:latest
        - llama3:70B
    """
    def __init__(self, model : str):
        self.model = model
    def get_model_response(self, prompt : str) -> str:
        output = ""
        for chunk in ollama.chat(model=self.model, messages=[{'role': 'user', 'content': prompt}], stream=True):
            if 'message' in chunk and 'content' in chunk['message']:
                line = chunk['message']['content']
                output += line
        return output

"""
Example of how to use
"""
# ai = llama3("llama3:latest")
# print(ai.get_model_response("Can you write me a code to generate fibonacci sequence of numbers"))