import sqlite3
import os

def check_if_db_exist(database : str):
    current_path = os.getcwd() + "/data/" + database
    if not os.path.exists(current_path):
        raise ValueError("Invalid filepath: " + current_path)

def check_if_table_exist(table_name : str, database : str) -> bool:
    check_if_db_exist(database)
    conn = sqlite3.connect(database)
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
    tables = set(cursor.fetchall())
    conn.close()
    return table_name in tables

def get_all_tables(database : str) -> bool:
    check_if_db_exist(database)
    conn = sqlite3.connect(database)
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

def create_table(database : str):
    check_if_db_exist(database)
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    # Create a table (only if it doesn’t already exist)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id TEXT NOT NULL,
        sender TEXT NOT NULL,
        text TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        apple_rowid INTEGER,
        is_spam INTEGER DEFAULT 0,
        responded INTEGER DEFAULT 0
    );
    """)
    # Commit changes and close
    conn.commit()
    conn.close()

