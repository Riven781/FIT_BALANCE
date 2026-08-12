from product_catalog_context.application.query.category_path_item import CategoryPathItem
from product_catalog_context.application.query.product_detail import PublicProductDetail
from product_catalog_context.domain.nutrition_facts import Nutrients, NutritionFacts, ReferenceQuantity


#def to_category_path_item():
#  pass

def to_product_detail(row):
  nutrients = Nutrients(
    fat=row['fat'],
    saturates=row['saturates'],
    carbohydrates=row['carbohydrates'],
    sugars=row['sugars'],
    protein=row['protein'],
    salt=row['salt'],
    fiber=row['fiber'])
  nutrition_facts = NutritionFacts(
    ReferenceQuantity(row['reference_amount'], row['reference_unit']),
    row['kcal'],
    nutrients=nutrients
  )
  return PublicProductDetail(product_id=row['id'], name=row['name'], brand_name=row['brand_name'], nutrition_facts=nutrition_facts, img_src=row['img_src'], category_path=to_category_path_item_list(row['category_str']))


def to_category_path_item_list(encoded_category_path):
  if encoded_category_path is not None:
    category_ids_str, category_names_str = encoded_category_path.split(':')
    category_ids = category_ids_str.split('|')
    category_names = category_names_str.split('|')
    return [CategoryPathItem(int(id), name) for id, name in zip(category_ids, category_names)]
  else:
    return []