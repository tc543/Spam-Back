import time
import os
from src import create_table, init_table, detect_incoming_messages, update_table


def spam_back(chat: any, is_spam: int):
    db_path = os.path.join(os.getcwd(), 'data/messages.db')
    table = "message_read_history"
    create_table(db_path, table)
    init_table(db_path, table, chat, False, is_spam)
    while True:
        time.sleep(1)
        print("polling")
        if detect_incoming_messages(db_path, table, chat):
            update_table(db_path, table, chat, False)
