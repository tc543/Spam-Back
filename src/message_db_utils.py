import sqlite3
import os
import json
from datetime import datetime
from src import extract_chats, extract_conversation, convert_conversation_to_text, llama3, generate_response, send_imessage
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

def init_summary_conversation(conversation: str, group_chat: bool, me: str, group_size: int = 0,):
    prompt = f"""
    You are one of the participants in the following conversation, referred to as {me}.

    Generate a clear and well-structured summary of the conversation. 
    Your goal is to capture the essential context so that future messages can be understood without rereading the entire chat.

    Organize your response into the following sections:
    - **Participants:** Identify who is involved and their general roles or perspectives.
    - **Main Topics:** Describe the key subjects or themes discussed.
    - **Intentions / Actions:** Summarize what each participant seems to be trying to achieve or express.
    - **Overall Summary:** Provide a concise narrative tying the conversation together.

    Keep it informative and coherent, detailed enough to preserve context, 
    but avoid unnecessary repetition or excessive length.

    Conversation:

    {conversation}
    """
    if group_chat:
        prompt += f"This is a group chat conversation of {group_size} people.\n\n"
    else:
        prompt += "This is a direct message.\n\n"
    llm = llama3("llama3:latest")
    return llm.get_model_response(prompt)

def update_summary_conversation(conversation: str, prev_summary : str, me: str):
    prompt = f"""
    You are one of the participants in the conversation, referred to as {me}.

    Below is the previous summary of the conversation so far:

    {prev_summary}

    Now, here are the new incoming messages:

    {conversation}

    Please update the summary to include the new information while maintaining context from the previous summary.

    Organize your updated summary into the following sections:
    - **Participants:** Update or confirm who is involved and their roles.
    - **Main Topics:** Reflect any new topics or developments.
    - **Intentions / Actions:** Note any changes in participants' goals, tone, or direction.
    - **Overall Summary:** Integrate the old and new information into one coherent summary that reflects the current state of the conversation.

    Keep it informative, logically structured, and moderately detailed, 
    ensuring it can serve as context for future messages without rereading the full chat.
    """

    """
    Might or might not need it, depending on how well llm generating without this information
    """
    # if group_chat:
    #     prompt += "Again, this is a group chat conversation of {group_size} people.\n"
    # else:
    #     prompt += "Again, this is a direct message.\n"                               # it will be easier to see the purpose in this summary when including context clues around
    llm = llama3("llama3:latest")
    return llm.get_model_response(prompt)
    
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
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    check_if_val_exists(db_path, "chat_id", chat_id, table)
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

def init_table(db_path: str, table: str, chat: any, group: bool):    
    check_if_table_exists(table, db_path)
    all_chats = extract_chats()
    for user_chat, group_size in all_chats:
        if group:
            if any == user_chat and group_size > 1:
                return
        else:
            if any == user_chat and group_size == 1:
                return
    if group:
        # TODO assert chat is group
        conversation = extract_conversation(chat[0], True, False)
        chat_mp = {}
        text, last_row = convert_conversation_to_text(conversation, chat_mp)
        init_summary = init_summary_conversation(text, True, chat_mp["Me"])
        insert_row_in_table(db_path, table, last_row, chat[0], init_summary, 0, chat_mp)
        response = generate_response(text, True)
        send_imessage(chat[0], response)
    else:
        # TODO assert chat is dm
        conversation = extract_conversation(chat, True, False)
        chat_mp = {}
        text, last_row = convert_conversation_to_text(conversation, chat_mp)
        init_summary = init_summary_conversation(text, True, chat_mp["Me"])
        insert_row_in_table(db_path, table, last_row, chat, init_summary, 0, chat_mp)
        response = generate_response(text, True)
        send_imessage(chat, response)

def update_table(db_path : str, table : str, chat: any, group: bool):
    check_if_table_exists(table, db_path)
    if group:
        curr_row = extract_row_from_table(db_path, table, chat[0])
        conversation = extract_conversation(chat, True, False, last_row=curr_row["row_id"])
        text, last_row = convert_conversation_to_text(conversation, curr_row["chat_mp"])
        updated_summary = update_summary_conversation(text, curr_row["summary"], curr_row["chat_mp"]["Me"])
        update_row_in_table(db_path, table, chat[0], last_row, updated_summary, curr_row["chat_mp"])
        response = generate_response(text, False, curr_row["summary"])
        send_imessage(chat[0], response)
    else:
        curr_row = extract_row_from_table(db_path, table, chat)
        conversation = extract_conversation(chat, False, False, last_row=curr_row["row_id"])
        text, last_row = convert_conversation_to_text(conversation, curr_row["chat_mp"])
        updated_summary = update_summary_conversation(text, curr_row["summary"], curr_row["chat_mp"]["Me"])
        update_row_in_table(db_path, table, chat, last_row, updated_summary, curr_row["chat_mp"])
        response = generate_response(text, False, curr_row["summary"])
        send_imessage(chat, response)

def detect_incoming_messages(db_path: str, table: str, chat: str, group: bool) -> bool:
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
