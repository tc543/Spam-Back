import sqlite3
import pandas as pd
import typedstream
from .read_imessage import *
from .llm_prompter import *
from .message_db_utils import *
db_path = '/Users/whusyki/Spam_Back/data/messages.db'
dm, group = extract_chats()
print(dm)
print(group)
table = "message_read_history"
# create_table(db_path, table)
init_table(db_path, table)