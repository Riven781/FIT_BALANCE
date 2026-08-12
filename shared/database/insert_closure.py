import json
import sqlite3

conn = sqlite3.connect('./shared/database/fit-balance-v2.db')
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON")


def get_category_node_id_by_name(name):
  cursor.execute(
      """
        SELECT id FROM ProductCategoryNode
        WHERE name = ?;
      """, (name,)
    )
  return cursor.fetchone()[0]

def set_product_category_ent(super, sub, depth):
  super_id = get_category_node_id_by_name(super)
  sub_id = get_category_node_id_by_name(sub)
  cursor.execute(
    """
      INSERT INTO ProductCategoryClosure(supercategory_id, subcategory_id, depth) VALUES (?, ?, ?)
    """, (super_id, sub_id, depth)
  )


with open("./api/products_hierarchy_2.json", "r", encoding='utf-8') as hierarchy_file:
  hierarchy = json.load(hierarchy_file)

  def set_category_depth(super, sublist, depth=1):
    if len(sublist) == 0:
      return
    for sub in sublist:

      set_product_category_ent(super, sub, depth)
      set_category_depth(super, hierarchy[sub]['subtypes'], depth + 1)


  for category in list(hierarchy):
    set_product_category_ent(category, category, 0)
    set_category_depth(category, hierarchy[category]['subtypes'])
    