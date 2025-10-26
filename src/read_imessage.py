import sqlite3
import pandas as pd
import typedstream

# Set up connection
conn = sqlite3.connect('/Users/whusyki/Library/Messages/chat.db') # make it parameter TODO
# Create a cursor object, a way to talk to the database through connection
c = conn.cursor()

query = """
SELECT
    message.ROWID,
    datetime(message.date / 1000000000 + strftime('%s', '2001-01-01'), 'unixepoch', 'localtime') AS message_date,
    message.is_from_me,
    message.text,
    message.attributedBody
FROM message
ORDER BY message_date DESC
LIMIT 100;
"""

# Enter our sql command in chat.db and return result, if any, in the cursor object
c.execute(query)
# Extract result into python variable
rows = c.fetchall()

def decode_attributed_body(data):
    '''
    Blob in attributedBody is serialized by Apple, this function helps unserialize it
    and return a perfect normal text with emojis

    Not sure if I need to have those 2 safe check, but keep it for now and can uncomment later
    if we do happen to run a test case of not safe checking
    '''
    # if not data:
    #     return None
    # if isinstance(data, memoryview):
    #     data = data.tobytes()
    return typedstream.unarchive_from_data(data).contents[0].value.value

# Printing the result
# Verifying can read others and my text message
for rowid, date, is_from_me, text, blob in rows:
    decoded_text = text or decode_attributed_body(blob)
    sender = "Me" if is_from_me else "Them"
    print(f"[{date}] ({sender}) {decoded_text}")

conn.close()
