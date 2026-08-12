import sqlite3


conn = sqlite3.connect('./shared/database/fit-balance-v2.db')

cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON")

cursor.execute(
  """
  INSERT INTO User(username, email, hashed_password) VALUES (?,?,?);
  """,
  ('XYZ', 'xyz@gmail.com', 'xxx')
)

conn.commit()
conn.close()