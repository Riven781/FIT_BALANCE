import json
import sqlite3

conn = sqlite3.connect('./shared/database/fit-balance-v2.db')

cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON")

create_table = """
CREATE TABLE IF NOT EXISTS IdSequence(
  name TEXT PRIMARY KEY,
  next_value INTEGER NOT NULL)
"""
cursor.execute(create_table)

init = """
INSERT INTO IdSequence VALUES
  ('product_category', 1)
"""
cursor.execute(init)

conn.commit()
conn.close()