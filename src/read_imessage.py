import sqlite3
import pandas as pd
import typedstream

def decode_attributed_body(data): # TODO write better spec
    '''
    Blob in attributedBody is serialized by Apple, this function helps unserialize it
    and return a perfect normal text with emojis
    '''
    if not data:
        return "[Message Unsent]"
    
    """
    Not sure if I need to have 1 safe check, but keep it for now and can uncomment later
    if we do happen to run a test case of not safe checking
    """
    # if isinstance(data, memoryview):
    #     data = data.tobytes()
    return typedstream.unarchive_from_data(data).contents[0].value.value

def extract_chats(c : sqlite3.Cursor) -> tuple[list[str], list[str]]: # TODO write a spec
    query = """
    SELECT
        chat.chat_identifier,
        COUNT(chat_handle_join.handle_id) AS num_participants
    FROM
        chat
        LEFT JOIN chat_handle_join ON chat.ROWID = chat_handle_join.chat_id
    GROUP BY
        chat.chat_identifier
    ORDER BY
        num_participants DESC;
    """
    c.execute(query)
    res = c.fetchall()
    dm = []
    group_chat = []
    for chat, group_size in res:
        if group_size > 1:
            group_chat.append(chat)
        else:
            dm.append(chat)
    return (dm, group_chat)

def extract_dm_conversation(c : sqlite3.Cursor, chat : str, group_chat : bool, most_recent : bool = True, limit : int = 20) -> pd.DataFrame: # TODO write a spec
    order_by = "DESC"
    if not most_recent:
        order_by = "ASC"
    query = f"""
    SELECT
        *
    FROM (
        SELECT
            datetime(message.date / 1000000000 + strftime("%s", "2001-01-01"), "unixepoch", "localtime") AS message_date,
            message.text,
            message.is_from_me,
            message.attributedBody,
            attachment.filename,
            handle.id
        FROM
            chat
            JOIN chat_message_join ON chat."ROWID" = chat_message_join.chat_id
            JOIN message ON chat_message_join.message_id = message."ROWID"
            JOIN handle ON message.handle_id = handle. "ROWID"
            LEFT JOIN message_attachment_join ON message."ROWID" = message_attachment_join.message_id
            LEFT JOIN attachment ON message_attachment_join.attachment_id = attachment."ROWID"
        WHERE
            chat_identifier = '{chat}'
        ORDER BY
            message_date {order_by}
        LIMIT {limit}
    )
    ORDER BY message_date ASC;
    """
    c.execute(query)
    rows = c.fetchall()
    messages = []
    for date, text, is_from_me, blob, attachment, sender_person in rows:
        decoded_text = text or decode_attributed_body(blob)
        sender = "Me" if is_from_me else sender_person
        if attachment == None:
            attachment = "[No attachment found]"
        else:
            attachment = "$HOME" + attachment[1:]
        messages.append({
            "Date": date,
            "Sender": sender,
            "Conversation": "[Group Chat]" if group_chat else "[Direct Message]",
            "Text": decoded_text,
            "Attachment": attachment
        })
    df = pd.DataFrame(messages, columns=["Date", "Sender", "Conversation", "Text", "Attachment"])

    """
    [Optional]
    Full screen for printing the entire table
    """
    # pd.set_option('display.max_columns', None)
    # pd.set_option('display.max_rows', None)
    # pd.set_option('display.max_colwidth', None)
    # pd.set_option('display.width', None)

    return df

def open_attachment(filepath : str):
    # TODO Implement terminal code that auto open an attachment, rather than coding it up in terminal by
    # open "filepath"
    # it might be in shell?
    pass

"""
Example of how to test these functions
Can comment/uncomment to play around
"""
# Set up connection
conn = sqlite3.connect('/Users/whusyki/Library/Messages/chat.db') # make it parameter TODO
# Create a cursor object, a way to talk to the database through connection
c1 = conn.cursor()
dm, group = extract_chats(c1)
print(dm)
print(group)
print(extract_dm_conversation(c1, dm[5], False, limit = 10))

conn.close()
