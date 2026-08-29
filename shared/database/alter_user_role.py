import json
import sqlite3

conn = sqlite3.connect('./shared/database/fit-balance-v2.db')

cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON")

alter = """
DROP TABLE UserRole;
"""
cursor.execute(alter)

alter = """
CREATE TABLE IF NOT EXISTS UserRole(
    user_id INTEGER NOT NULL,
    role TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES User(id)
      ON DELETE CASCADE,
    PRIMARY KEY(user_id, role)
   ) STRICT;
"""
cursor.execute(alter)

conn.commit()
conn.close()