import json
import sqlite3

conn = sqlite3.connect('./shared/database/fit-balance-v2.db')

cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON")

change = """
  DROP TABLE IF EXISTS ProductCategoryAssignmentTask;

  CREATE TABLE IF NOT EXISTS ProductCategoryAssignmentTask(
    id INTEGER PRIMARY KEY,
    product_id INTEGER NOT NULL,
    hierarchy_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    status TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES Product(id)
      ON DELETE CASCADE,
    FOREIGN KEY (hierarchy_id) REFERENCES ProductCategoryHierarchy(id)
      ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES User(id)
      ON DELETE CASCADE,
    UNIQUE (product_id, hierarchy_id)
  ) STRICT;
"""
cursor.executescript(change)


conn.commit()
conn.close()