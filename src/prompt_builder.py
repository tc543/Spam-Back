from .llm_prompter import *


def generate_response(conversation: str, initial: bool, summary: str | None = None) -> str:
    prompt = """
    """
    if initial:
        prompt += f"""
        Read the following conversation and write a natural, contextually appropriate reply that smoothly continues the discussion. 
        Only output the reply text itself — do not include explanations, notes, or formatting.

        Conversation:

        {conversation}
        """
    else:
        prompt = f"""
        Here is a summary of the conversation so far:

        {summary}

        Below are the new incoming messages:

        {conversation}

        Using the context from the summary and the new messages, write a natural and contextually appropriate reply that continues the conversation smoothly. 
        Only output the reply text itself — do not include explanations, formatting, or any additional commentary.
        """
    llm = llama3("llama3:latest")
    return llm.get_model_response(prompt)
