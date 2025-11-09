import time
from src import *


def spam_back(chat: any):
    db_path = os.path.join(os.getcwd(), 'data/messages.db')
    table = "message_read_history"
    create_table(db_path, table)
    init_table(db_path, table, chat, False)
    while True:
        time.sleep(1)
        print("polling")
        if detect_incoming_messages(db_path, table, chat, False):
            update_table(db_path, table, chat, False)

