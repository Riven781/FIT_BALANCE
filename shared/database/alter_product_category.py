import json
import sqlite3

conn = sqlite3.connect('./shared/database/fit-balance-v2.db')

cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON")

alter = """
ALTER TABLE ProductCategoryNode ADD COLUMN source_node_id INTEGER DEFAULT NULL REFERENCES ProductCategoryNode(id)
    ON DELETE SET NULL;
"""
cursor.execute(alter)


conn.commit()
conn.close()