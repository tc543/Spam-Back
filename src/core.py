import sqlite3
import pandas as pd
import typedstream
import time
from .read_imessage import *
from .llm_prompter import *
from .message_db_utils import *

db_path = os.path.join(os.getcwd(), 'data/messages.db') # TODO make it generalize
table = "message_read_history"

"""SENSITIVE, DELETE BEFORE COMMIT AND PUSH TO GITHUB"""
chat = "+1" # Add a 1 for US, also need to use python phone package function to help normalize it
"""SENSITIVE, DELETE BEFORE COMMIT AND PUSH TO GITHUB"""


"""
Initialize database and table if empty
OR
First time talking to someone with the AI
"""
create_table(db_path, table)
init_table(db_path, table, chat, False)

while True:
    time.sleep(1)
    print("polling")
    if detect_incoming_messages(db_path, table, chat, False):
        update_table(db_path, table, chat, False)
