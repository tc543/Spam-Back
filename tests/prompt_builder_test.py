import pytest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import generate_response, is_safe_reply, sanitize_reply, generate_spammer_response, init_spammer_summary_conversation, safe_wrapper

@pytest.fixture
def basic_conversation():
    prompt = """
        Person 0 said I want to eat an ice cream, but should I buy a tub or individual small box cup.
        Person John Smith said you definitely should buy a tub because it's way cheaper than small box of cup.
        Person 0 said nah you're capping, it should be same price
    """
    return prompt

@pytest.fixture
def spammer_init_conversation():
    prompt = [
        """
        Person 1 said Free entry in 2 a wkly comp to win FA Cup final tkts 21st May 2005. Text FA to 87121 to receive entry question(std txt rate)T&C's apply 08452810075over18's
        """,
        """
        FreeMsg Hey there darling it's been 3 week's now and no word back! I'd like some fun you up for it still? Tb ok! XxX std chgs to send, å£1.50 to rcv
        """,
        """
        WINNER!! As a valued network customer you have been selected to receivea å£900 prize reward! To claim call 09061701461. Claim code KL341. Valid 12 hours only.
        """
    ]
    return prompt

@pytest.fixture
def spammer_summary_text():
    prompt = [
        """
        Person 1 said Free entry in 2 a wkly comp to win FA Cup final tkts 21st May 2005. Text FA to 87121 to receive entry question(std txt rate)T&C's apply 08452810075over18's
        Person John Smith said Wow, that sounds like an amazing opportunity! I've always loved football. Do you think they'll have a chance to win it this year? Also, what's the typical size of the FA Cup final tickets - are they A4 or A3-sized? And, by the way, do you live near Wembley Stadium or will you be watching from elsewhere?
        Person 1 said Yes mate, it's going to be huge this year! Just text FA to 87121 and you'll get your entry straight away — they'll send the question back instantly. Winners get VIP seats at Wembley, travel included!
        Person John Smith said That's a big prize! I'm curious, what makes this year's competition so special? Is there a particular team or player that's expected to shine? And by the way, do you have any recommendations for good pubs near Wembley Stadium?
        """
    ]
    return prompt

# @pytest.mark.skip(reason="Not focusing this test")
def test_llm_normal_response(basic_conversation):
    print("\n")
    result_basic = generate_response(basic_conversation, True, "John Smith")
    print(result_basic)
    assert True

# @pytest.mark.skip(reason="Not focusing this test")
def test_llm_init_spam_response(spammer_init_conversation):
    print("\n")
    for prompt in spammer_init_conversation:
        print('-' * 140)
        reply = generate_spammer_response(prompt, True, "John Smith")
        safe, issues = is_safe_reply(reply)
        if not safe:
            print("⚠️ unsafe content detected:", issues)
            reply = sanitize_reply(reply)
        print("Spammer text: \n")
        print(prompt + "\n")
        print("LLM response: \n")
        print(reply)
    assert True

# @pytest.mark.skip(reason="Not focusing this test")
def test_llm_update_spam_response(spammer_summary_text):
    print("\n")
    for prompt in spammer_summary_text:
        print('-' * 140)
        summary = init_spammer_summary_conversation(prompt, False, "John Smith")
        s = """
        Yeah, mate, this year's all about the energy — everyone's talking about it! Honestly, it's a once-in-a-lifetime shot. If you text FA to 87121, you'll get the entry question straight away — it only takes a sec. And if you win, you'll be right in the middle of the action at Wembley! As for pubs, The Green Man near the stadium's always packed before the match — great spot for a pint!
        """
        reply = generate_spammer_response(s, False, "John Smith", summary)
        print(summary)
        print('-' * 140)
        print(safe_wrapper(reply))
    assert True

# command to run: pytest -s tests/prompt_builder_test.py