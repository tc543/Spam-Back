import sqlite3
import pandas as pd
import datetime

conn = sqlite3.connect('/Users/whusyki/Library/Messages/chat.db')
c = conn.cursor()

other_number = "+"  # the phone number you want

cmd_msgs = f"""
SELECT 
    m.ROWID AS message_id,
    m.text,
    m.handle_id,
    CASE 
        WHEN m.handle_id IS NULL THEN 'me' 
        ELSE 'other' 
    END AS sender_label,
    datetime(m.date + strftime('%s','2001-01-01'), 'unixepoch') AS date_utc,
    c.chat_identifier
FROM message m
JOIN chat_message_join cmj ON m.ROWID = cmj.message_id
JOIN chat c ON cmj.chat_id = c.ROWID
WHERE c.chat_identifier = '{other_number}'
ORDER BY m.date
"""

c.execute(cmd_msgs)
df_msgs = pd.DataFrame(c.fetchall(), columns=["id", "text", "handle_id", "sender_label", "time", "chat"])
print(df_msgs)
