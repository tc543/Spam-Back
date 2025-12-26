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
    def get_model_response(self, prompt : str, background : str = "") -> str:
        output = ""
        incoming_input = [
            {"role": "system", "content": background},
            {"role": "user", "content": prompt}
        ]
        for chunk in ollama.chat(model=self.model, messages=incoming_input, stream=True):
            if 'message' in chunk and 'content' in chunk['message']:
                line = chunk['message']['content']
                output += line
        return output
