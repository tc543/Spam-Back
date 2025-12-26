import time
import os
from src import create_table, init_table, detect_incoming_messages, update_table


def spam_back(chat: any, is_spam: int):
    db_path = os.path.join(os.getcwd(), 'backend/data/messages.db')
    table = "message_read_history"
    print("Creating database table...")
    create_table(db_path, table)
    print('-' * 140)
    print("Setting up table and inserting records...")
    init_table(db_path, table, chat, False, is_spam)
    print('-' * 140)
    while True:
        time.sleep(1)
        print("polling")
        if detect_incoming_messages(db_path, table, chat):
            print('-' * 140)
            print("New message detected.")
            update_table(db_path, table, chat, False)
            print('-' * 140)

