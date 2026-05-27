import sqlite3
import json

conn = sqlite3.connect('./api/database/fit-balance.db')

cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON")

product_table_query = """
  CREATE TABLE IF NOT EXISTS Product (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    brand TEXT,
    kcal REAL,
    fat REAL,
    saturates REAL,
    carbohydrates REAL,
    sugars REAL,
    protein REAL,
    salt REAL,
    fiber REAL,
    ingredients TEXT,
    allergy_recommendations TEXT,
    reference_amount INTEGER,
    reference_unit TEXT,
    img_src TEXT,
    category_id INTEGER,
    FOREIGN KEY (category_id) REFERENCES ProductCategory(id)
      ON DELETE SET NULL
  );
"""

product_category_table_query = """
  CREATE TABLE IF NOT EXISTS ProductCategory(
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
  );
"""

product_category_closure_query = """
  CREATE TABLE IF NOT EXISTS ProductCategoryClosure(
    supercategory_id INTEGER,
    subcategory_id INTEGER,
    depth INTEGER NOT NULL,

    PRIMARY KEY (supercategory_id, subcategory_id)

    FOREIGN KEY (supercategory_id) REFERENCES ProductCategory(id)
      ON DELETE CASCADE,
    FOREIGN KEY (subcategory_id) REFERENCES ProductCategory(id)
      ON DELETE CASCADE
  );
"""

cursor.execute(product_category_table_query)
cursor.execute(product_table_query)
cursor.execute(product_category_closure_query)

#with open("./api/products_hierarchy.json", "r", encoding='utf-8') as hierarchy_file:
#  hierarchy = json.load(hierarchy_file)
#  hierarchy_list = [(row,) for row in list(hierarchy)]
#  cursor.executemany(
#    """
#      INSERT INTO ProductCategory (name) VALUES(?)
#    """, hierarchy_list
#  )
#cursor.execute("SELECT * FROM ProductCategory")

def get_category_id_by_name(name):
  cursor.execute(
      """
        SELECT id FROM ProductCategory
        WHERE name = ?;
      """, (name,)
    )
  return cursor.fetchone()[0]

def set_product_category_ent(super, sub, depth):
  super_id = get_category_id_by_name(super)
  sub_id = get_category_id_by_name(sub)
  print("INSERT closure:", super_id, sub_id, depth)
  cursor.execute(
    """
      INSERT INTO ProductCategoryClosure(supercategory_id, subcategory_id, depth) VALUES (?, ?, ?)
    """, (super_id, sub_id, depth)
  )


cursor.execute(
  """
    SELECT super.name, sub.name, depth FROM ProductCategoryClosure AS pcc
    INNER JOIN ProductCategory AS super ON pcc.supercategory_id = super.id
    INNER JOIN ProductCategory AS sub ON pcc.subcategory_id = sub.id
    WHERE super.name = 'Owoce i warzywa';
  """
)
print(cursor.fetchall())


cursor.execute(
  """
  SELECT * FROM Product as p
  INNER JOIN ProductCategory as pc ON p.category_id = pc.id 
  WHERE p.id < 5
"""
)

for row in cursor.fetchall():
  print(row)



#with open("./api/products.json", "r", encoding='utf-8') as products_file:
#  products = json.load(products_file)
#  for product in products:
#    category = product['category'][-1] if len(product['category']) > 1 else None
#    category_id = get_category_id_by_name(category) if category is not None else None
#    cursor.execute(
#      """
#        INSERT INTO Product(id, name, brand, kcal, fat, saturates, carbohydrates, sugars, protein, salt, fiber, ingredients, allergy_recommendations, reference_amount, reference_unit, img_src, category_id)
#        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#      """, (product['id'], product['name'], product['brand'], product['kcal'], product['fat'], product['saturates'], product['carbohydrates'], product['sugars'], product['protein'], product['salt'], product['fiber'], product['ingredients'], product['allergy_recommendations'], product['reference_amount'], product['reference_unit'], product['img_src'], category_id)
#    )




"""

with open("./api/products_hierarchy_2.json", "r", encoding='utf-8') as hierarchy_file:
  hierarchy = json.load(hierarchy_file)

  def set_category_depth(super, sublist, depth=1):
    if len(sublist) == 0:
      return
    for sub in sublist:
      print(f"Dodaje super {super} sub: {sub}, czyli {get_product_id_by_name(sub)}")

      set_product_category_ent(super, sub, depth)
      set_category_depth(super, hierarchy[sub]['subtypes'], depth + 1)


  for category in list(hierarchy):
    set_product_category_ent(category, category, 0)
    print(category)
    print(hierarchy[category]['subtypes'])
    set_category_depth(category, hierarchy[category]['subtypes'])
    

"""


#print(cursor.fetchall())

  
conn.commit()
conn.close()


#with open("./products.json", "r", encoding='utf-8'):
  