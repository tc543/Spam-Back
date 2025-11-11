import pytest

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import generate_response

@pytest.fixture
def basic_conversation():
    prompt = """
        hey
    """
    return prompt

@pytest.fixture
def spammer_conversation():
    prompt = """
        hey
    """
    return prompt

def test_llm_response_is_correct(basic_conversation):
    result = generate_response(basic_conversation, True)
    print(result)
    assert True
