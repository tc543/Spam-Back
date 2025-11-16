import sqlite3
import os
import json
from datetime import datetime
from src import extract_chats, extract_conversation, convert_conversation_to_text, generate_response, send_imessage, init_summary_conversation, update_summary_conversation, generate_spammer_response, update_spammer_summary_conversation, init_spammer_summary_conversation
from config import config


def check_if_db_exists(db_path : str):
    if not os.path.exists(db_path):
        raise ValueError("Invalid filepath: " + db_path)

def check_if_table_exists(table_name : str, db_path : str):
    check_if_db_exists(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    query = """
    SELECT
        name
    FROM
        sqlite_master
    WHERE
        type='table'
    """
    cursor.execute(query)
    tables = set([t[0] for t in cursor.fetchall()])
    conn.close()
    if table_name not in tables:
        raise ValueError("Invalid table: " + table_name + " in db_path")

def check_if_column_exists(db_path: str, table: str, column: str) -> bool:
    check_if_table_exists(table, db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table})")
    columns = set([col_info[1] for col_info in cursor.fetchall()])
    conn.close()
    if not column in columns:
        raise ValueError("Column " + column + " doesn't exist in table " + table)

def check_if_val_exists(db_path: str, col: str, val, table: str) -> bool:
    check_if_table_exists(table, db_path)
    check_if_column_exists(db_path, table, col)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    query = f"SELECT 1 FROM {table} WHERE {col} = ? LIMIT 1"
    cursor.execute(query, (val,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

def get_all_tables(db_path : str) -> bool:
    check_if_db_exists(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    query = """
    SELECT
        name
    FROM
        sqlite_master
    WHERE
        type='table'
    """
    cursor.execute(query)
    tables = cursor.fetchall()
    conn.close()
    return tables

def create_table(db_path : str, table : str):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {table} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        row_id INTEGER NOT NULL,
        chat_id TEXT NOT NULL,
        summary TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        is_spam INTEGER DEFAULT 0,
        chat_mp TEXT
    );
    """)
    conn.commit()
    conn.close()

def insert_row_in_table(
    db_path: str,
    table: str,
    row_id: int,
    chat_id: str,
    summary: str,
    is_spam: int = 0,
    chat_mp: dict = None
):
    if chat_mp is None:
        raise ValueError("Invalid conversation") # Can this case actually happen? Maybe we should try system testing
    if check_if_val_exists(db_path, "chat_id", chat_id, table):
        print(f"The conversation {chat_id} has already initialized")
        return
    chat_mp_json = json.dumps(chat_mp)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"""
        INSERT INTO {table}
        (row_id, chat_id, summary, timestamp, is_spam, chat_mp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        row_id,
        chat_id,
        summary,
        datetime.now().isoformat(timespec='seconds'),
        is_spam,
        chat_mp_json
    ))
    conn.commit()
    conn.close()
    

def update_row_in_table(
    db_path: str,
    table: str,
    chat_id: int,
    row_id: int,
    summary: str,
    chat_mp: dict
):
    """
    TODO
    Might have to add is_spam parameter to update from regular to spammer or vice versa
    This is for switching spammer value 0 or 1
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    if not check_if_val_exists(db_path, "chat_id", chat_id, table):
        raise ValueError("Row does not exist in the first place")
    fields = []
    values = []
    fields.append("summary = ?")
    values.append(summary)
    fields.append("chat_mp = ?")
    values.append(json.dumps(chat_mp))
    fields.append("row_id = ?")
    values.append(row_id)
    fields.append("timestamp = ?")
    values.append(datetime.now().isoformat(timespec='seconds'))
    values.append(chat_id)
    sql = f"UPDATE {table} SET {', '.join(fields)} WHERE chat_id = ?"
    cursor.execute(sql, values)
    conn.commit()
    conn.close()

def extract_row_from_table(db_path: str, table: str, chat_id: str) -> dict | None:
    check_if_table_exists(table, db_path)
    check_if_val_exists(db_path, "chat_id", chat_id, table)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    sql = f"SELECT * FROM {table} WHERE chat_id = ?"
    cursor.execute(sql, (chat_id,))
    row = cursor.fetchone()
    conn.close()
    row_dict = dict(row)
    if "chat_mp" in row_dict and row_dict["chat_mp"] is not None:
        row_dict["chat_mp"] = json.loads(row_dict["chat_mp"])
    return row_dict

def init_table(db_path: str, table: str, chat: any, group: bool, is_spam: int):
    check_if_table_exists(table, db_path)
    if check_if_val_exists(db_path, "chat_id", chat, table):
        return
    chat_mp = {}
    text = ""
    if group:
        chat = chat[0]
        # TODO assert chat is group
        conversation = extract_conversation(chat, True, False)
        text, last_row = convert_conversation_to_text(conversation, chat_mp)
    else:
        # TODO assert chat is dm
        conversation = extract_conversation(chat, False, False)
        text, last_row = convert_conversation_to_text(conversation, chat_mp)
    init_summary = ""
    response = ""
    if is_spam == 1:
        response = generate_spammer_response(text, True, chat_mp["Me"])
        if group:
            init_summary = init_spammer_summary_conversation(text, True, config['default']['person_name'])
        else:
            init_summary = init_spammer_summary_conversation(text, False, config['default']['person_name'])
    else:
        response = generate_response(text, True, chat_mp["Me"])
        if group:
            init_summary = init_summary_conversation(text, True, config['default']['person_name'])
        else:
            init_summary = init_summary_conversation(text, False, config['default']['person_name'])
    insert_row_in_table(db_path, table, last_row, chat, init_summary, is_spam, chat_mp)
    if group:
        send_imessage(chat, response, True)
    else:
        send_imessage(chat, response)


def update_table(db_path : str, table : str, chat: any, group: bool):
    check_if_table_exists(table, db_path)
    if group:
        chat = chat[0]
        curr_row = extract_row_from_table(db_path, table, chat)
        conversation = extract_conversation(chat, True, False, last_row=curr_row["row_id"])
    else:
        curr_row = extract_row_from_table(db_path, table, chat)
        conversation = extract_conversation(chat, False, False, last_row=curr_row["row_id"])
    
    text, last_row = convert_conversation_to_text(conversation, curr_row["chat_mp"])
    print("New incoming text: ")
    print(text)
    old_summary = curr_row["summary"]
    if curr_row["is_spam"] == 1:
        updated_summary = update_spammer_summary_conversation(text, curr_row["summary"], curr_row["chat_mp"]["Me"])
        update_row_in_table(db_path, table, chat, last_row, updated_summary, curr_row["chat_mp"])
        response = generate_spammer_response(text, False, curr_row["chat_mp"]["Me"], old_summary)
    else:
        updated_summary = update_summary_conversation(text, curr_row["summary"], curr_row["chat_mp"]["Me"])
        update_row_in_table(db_path, table, chat, last_row, updated_summary, curr_row["chat_mp"])
        response = generate_response(text, False, curr_row["chat_mp"]["Me"], old_summary)
    
    print("New reponse text: ")
    print(response)
    send_imessage(chat, response)

def detect_incoming_messages(db_path: str, table: str, chat: str) -> bool:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT
            *
        FROM
            {table}
        WHERE
            chat_id = ?
        ORDER BY
            row_id DESC
        LIMIT 1
    """,
        (chat,)
    )
    row = cursor.fetchone()
    last_row_id = row["row_id"]
    conn.close()
    conn = sqlite3.connect(config['file_path']['chat_db_path'])
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = f"""
    SELECT
        message."ROWID" AS row_id
    FROM
        chat
        JOIN chat_message_join ON chat."ROWID" = chat_message_join.chat_id
        JOIN message ON chat_message_join.message_id = message."ROWID"
    WHERE
        chat_identifier = '{chat}'
        AND message.is_from_me = 0
    ORDER BY
        message.date DESC
    LIMIT 1
    """
    cursor.execute(query)
    result = cursor.fetchone()
    if result:
        return result["row_id"] > last_row_id
    return False
