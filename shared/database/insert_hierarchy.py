import sqlite3
import json

conn = sqlite3.connect('./shared/database/fit-balance-v2.db')

cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON")

cursor.execute(
  """
    INSERT INTO ProductCategoryHierarchy (status, published_at)
    VALUES ('ACTIVE', CURRENT_TIMESTAMP);
  """
)

conn.commit()
conn.close()