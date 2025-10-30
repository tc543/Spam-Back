import sqlite3
import os
from .read_imessage import *
from .llm_prompter import *
import json
from datetime import datetime

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

def init_summary_conversation(df, group_chat : bool, group_size : int = 0):
    prompt = """
    Generate a clear and well-detailed summary of the following conversation. 
    Include enough information about the main topics, participants, 
    and their intentions so that future incoming messages can be understood without re-reading the entire chat. 
    Keep it informative but not overly long\n\n.
    """
    chat_mp = {}
    last_row = -1
    if group_chat:
        prompt += f"This is a group chat conversation of {group_size} people.\n\n"
    else:
        prompt += "This is a direct message.\n\n"
    for row in df.itertuples(index=False):
        last_row = row.Row_ID
        if row.Sender not in chat_mp:
            chat_mp[row.Sender] = len(chat_mp)
        prompt += "Person " + str(chat_mp[row.Sender]) + " said " + row.Text + "\n"
        """
        TODO
        Add attachment response into this conversation
        """
        # if row.Attachment != "[No attachment found]":
        #     prompt += "In addition to the text, person " + chat_mp[row.Sender] + " add an attachment to it and the attachment is about "
        #     + " Insert Attachment Summary or something " # TODO, add a summary of what the attachment is, purpose maybe no need to add bc
        #                                                  # it will be easier to see the purpose in this summary when including context clues around
    llm = llama3("llama3:latest")
    return (llm.get_model_response(prompt), chat_mp, last_row)

def update_summary_conversation(df, chat_mp : dict, prev_summary : str, group_chat : bool, group_size : int = 0):
    prompt = f"""
    Here is the previous summary of the conversation from the last time it was read:

    {prev_summary}

    Now, here are the new incoming messages:


    """
    last_row = -1
    # if group_chat:
    #     prompt += "Again, this is a group chat conversation of {group_size} people.\n"
    # else:
    #     prompt += "Again, this is a direct message.\n"
    for row in df.itertuples(index=False):
        last_row = row.Row_ID
        if row.Sender not in chat_mp:
            chat_mp[row.Sender] = len(chat_mp)
        prompt += "Person " + str(chat_mp[row.Sender]) + " said " + row.Text + "\n"
        """
        TODO
        Add attachment response into this conversation
        """
        # if row.Attachment != "[No attachment found]":
        #     prompt += "In addition to the text, person " + chat_mp[row.Sender] + " add an attachment to it and the attachment is about "
        #     + " Insert Attachment Summary or something " # TODO, add a summary of what the attachment is, purpose maybe no need to add bc
        #                                                  # it will be easier to see the purpose in this summary when including context clues around
    prompt += """

    Please generate an updated summary that incorporates the new messages while keeping the previous context. 
    The summary should provide enough detail about the main topics, participants, and their intentions so that future messages can be understood without rereading the entire conversation. 
    Keep it informative but concise, avoiding unnecessary repetition.
    """
    llm = llama3("llama3:latest")
    return (llm.get_model_response(prompt), chat_mp, last_row)
    
def insert_row_in_table(
    db_path: str,
    table: str,
    row_id: int,
    chat_id: str,
    summary: str,
    is_spam: int = 0,
    chat_mp: dict = None
):
    print(chat_id)
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
    chat_mapping: dict
):
    """
    TODO
    Might have to add is_spam parameter to update from regular to spammer or vice versa
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    check_if_val_exists(db_path, table, "chat_id", chat_id)
    fields, values = []
    fields.append("summary = ?")
    values.append(summary)
    fields.append("chat_mapping = ?")
    values.append(json.dumps(chat_mapping))
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

def init_table(db_path : str, table : str):    
    check_if_table_exists(table, db_path)
    dm, group = extract_chats()
    # for chat in dm:
    #     conversation = extract_conversation(chat, False)
    #     init_summary, chat_mp, last_row = init_summary_conversation(conversation, False)
    #     insert_row_in_table(db_path, table, last_row, chat, init_summary, 0, chat_mp)
    for g in group:
        print(g)
        conversation = extract_conversation(g[0], True)
        init_summary, chat_mp, last_row = init_summary_conversation(conversation, True, g[1])
        insert_row_in_table(db_path, table, last_row, g[0], init_summary, 0, chat_mp)

def update_table(db_path : str, table : str):
    check_if_table_exists(table, db_path)
    dm, group = extract_chats()
    for chat in dm:
        curr_row = extract_row_from_table(db_path, table, chat)
        conversation = extract_conversation(chat, False, curr_row["row_id"])
        updated_summary, updated_chat_mp, new_last_row = update_summary_conversation(conversation, curr_row["chat_mp"], curr_row["summary"], False)
        update_row_in_table(db_path, table, chat, new_last_row, updated_summary, updated_chat_mp)
    for g in group:
        curr_row = extract_row_from_table(db_path, table, g[0])
        conversation = extract_conversation(g[0], False, curr_row["row_id"])
        updated_summary, updated_chat_mp, new_last_row = update_summary_conversation(conversation, curr_row["chat_mp"], curr_row["summary"], True, g[1])
        update_row_in_table(db_path, table, chat, new_last_row, updated_summary, updated_chat_mp)