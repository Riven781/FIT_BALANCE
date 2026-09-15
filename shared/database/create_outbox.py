import sqlite3

conn = sqlite3.connect('./shared/database/fit-balance-v2.db')

cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON")

outbox_table_query = """
  CREATE TABLE IF NOT EXISTS OutboxMessage (
    id INTEGER PRIMARY KEY,
    event_type TEXT NOT NULL,
    payload TEXT NOT NULL,
    occurred_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    processed_at TEXT,
    attempts INTEGER DEFAULT 0
  );
"""

if __name__ == '__main__':
  cursor.execute(outbox_table_query)
conn.commit()
conn.close()