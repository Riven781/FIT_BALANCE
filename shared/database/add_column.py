from os import name
import sqlite3
import json

conn = sqlite3.connect('./api/database/fit-balance.db')

cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON")

POLISH_CHARS = {
    "ą": "a",
    "ć": "c",
    "ę": "e",
    "ł": "l",
    "ń": "n",
    "ó": "o",
    "ś": "s",
    "ż": "z",
    "ź": "z",
    "Ą": "A",
    "Ć": "C",
    "Ę": "E",
    "Ł": "L",
    "Ń": "N",
    "Ó": "O",
    "Ś": "S",
    "Ż": "Z",
    "Ź": "Z",
}


cursor.execute(
  """
  ALTER TABLE Product
  ADD COLUMN name_search_standard TEXT DEFAULT '';
  """
)



cursor.execute("""SELECT id, name FROM Product""")
products = cursor.fetchall()

for id, name in products:
  name_translated = name.lower().translate(str.maketrans(POLISH_CHARS))
  cursor.execute(""" 
    UPDATE Product
    SET name_search_standard = ?
    WHERE id = ?
""", (name_translated, id))


conn.commit()
conn.close()