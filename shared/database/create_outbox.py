import sqlite3

conn = sqlite3.connect('./shared/database/fit-balance-v2.db')

cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON")

outbox_table_query = """
  DROP TABLE IF EXISTS OutboxMessage;
  CREATE TABLE OutboxMessage (
    id INTEGER PRIMARY KEY,
    message_type TEXT NOT NULL,
    message_name TEXT NOT NULL,
    payload TEXT NOT NULL,
    occurred_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    processed_at TEXT,
    retry_count INTEGER DEFAULT 0
  );
"""

if __name__ == '__main__':
  cursor.executescript(outbox_table_query)
conn.commit()
conn.close()