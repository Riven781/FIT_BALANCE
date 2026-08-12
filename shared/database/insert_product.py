import sqlite3
import json

conn = sqlite3.connect('./shared/database/fit-balance-v2.db')

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

def get_category_node_id_by_name(name):
  cursor.execute(
      """
        SELECT id FROM ProductCategoryNode
        WHERE name = ?;
      """, (name,)
    )
  return cursor.fetchone()[0]


with open("./shared/products.json", "r", encoding='utf-8') as products_file:
  products = json.load(products_file)
  for product in products:
    category = product['category'][-1] if len(product['category']) > 1 else None
    category_id = get_category_node_id_by_name(category) if category is not None else None
    name_translated = product['name'].lower().translate(str.maketrans(POLISH_CHARS))

    cursor.execute(
      """
        INSERT INTO Product(id, name, brand_name, kcal, fat, saturates, carbohydrates, sugars, protein, salt, fiber, ingredients, allergy_recommendations, reference_amount, reference_unit, img_src, name_search_standard)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      """, (product['id'], product['name'], product['brand'], product['kcal'], product['fat'], product['saturates'], product['carbohydrates'], product['sugars'], product['protein'], product['salt'], product['fiber'], product['ingredients'], product['allergy_recommendations'], product['reference_amount'], product['reference_unit'], product['img_src'], name_translated)
    )

    product_id = cursor.lastrowid
    if category_id is not None:
      cursor.execute(
        """
          INSERT INTO ProductCategoryAssignment (product_id, node_id)
          VALUES (?, ?)
        """, (product_id, category_id)
      )

conn.commit()
conn.close()