import json
import sqlite3
#python shared/database/outbox.py       
conn = sqlite3.connect('./shared/database/fit-balance-v2.db')

cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON")

payload = {
  'event_type' : 'product_category_changed_in_hierarchy',
  'changed_by' : None,
  'new_category_id' : 3,
  'old_category_id' : 1,
  'hierarchy_id' : 1,
  'product_id' : 1
}

json_payload = json.dumps(payload)

insert_ = """
  INSERT INTO OutboxMessage (event_type, payload)  VALUES 
  (?, ?);
"""

if __name__ == '__main__':
  cursor.execute(insert_, ['product_category_changed_in_hierarchy', json_payload])
conn.commit()
conn.close()