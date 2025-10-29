import sqlite3
import pandas as pd
import typedstream
from .read_imessage import *
from .llm_prompter import *

# Set up connection
conn = sqlite3.connect('/Users/whusyki/Library/Messages/chat.db') # make it parameter TODO
# Create a cursor object, a way to talk to the database through connection
c1 = conn.cursor()
dm, group = extract_chats(c1)

