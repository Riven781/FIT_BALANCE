import json
import sqlite3

conn = sqlite3.connect('./shared/database/fit-balance-v2.db')

cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON")

with open("./shared/products_hierarchy.json", "r", encoding='utf-8') as hierarchy_file:
  hierarchy = json.load(hierarchy_file)
  product_categories = list(hierarchy)
  for category_name in product_categories:

    cursor.execute(
      """
        INSERT INTO ProductCategoryNode (name, parent_id, hierarchy_id) 
        VALUES ( ?, ?, ?)
      """, ( category_name, None, 1)
    )
  for category_name in product_categories:
    supertype_name = hierarchy[category_name].get('supertypes')
    if supertype_name:
      cursor.execute(
        """
          UPDATE ProductCategoryNode
          SET parent_id = (
            SELECT id FROM ProductCategoryNode
            WHERE name = ?
          )
          WHERE name = ?
        """,
        (supertype_name[0] ,category_name)
      )

conn.commit()
conn.close()