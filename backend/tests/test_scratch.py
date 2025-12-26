import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import *


def read_imessage():
    """
    Example of how to test these functions
    Can comment/uncomment to play around
    """
    res = extract_chats()
    print(res)
    print(extract_conversation(res[9][0], False, False, limit = 10, full_view=True))

def write_imessage():
    msg = "Wassup indeed! 😄 Dog mode activated! So, what's been on your mind lately? Any new hobbies, games, or shows you're into? 🐾📺"
    chat_identifier = '+1'
    send_imessage(chat_identifier, msg)

def test_write_to_group():
    msg = """
    Testing group chat
    Send message
    """
    chat_identifier = ''
    send_imessage(chat_identifier, msg, True)

def llm_prompter():
    """
    Example of how to use
    """
    ai = llama3("llama3:latest")
    print(ai.get_model_response("Can you write me a code to generate fibonacci sequence of numbers with no explaation", "You have to write it recursively"))

def message_db_utils():
    # print(check_if_table_exist("message_read_history", "messages.db"))
    # print(get_all_tables("messages.db"))
    # check_if_db_exist("messages.dbs")
    path = os.path.join(os.getcwd(), "data", "messages.db")
    create_table(path)

def test_config():
    print(config['default']['person_name'])

if __name__ == "__main__":
    print("Main: ")
    # Uncomment the function you want to run and it will be running helper function
    # in the file based on function name
    # read_imessage()
    write_imessage()
    # test_write_to_group()
    # test_config()
    # llm_prompter()
    # message_db_utils()
