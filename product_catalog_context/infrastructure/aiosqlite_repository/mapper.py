from product_catalog_context.domain.nutrition_facts import Nutrients, NutritionFacts, ReferenceQuantity
from product_catalog_context.domain.product import Product


class ProductMapper:
  def __init__(self):
    pass

  @staticmethod
  def to_storage_dict(product: Product):
    print(product.nutrition_facts)
    out_dict = {}
    if product.id is not None:
      out_dict['id'] = product.id
    out_dict['name'] = product.name
    out_dict['brand'] = product.brand_name
    out_dict['category_id'] = product.category_id
    out_dict['img_src'] = product.img_src
    out_dict['ingredients'] = product.ingredients
    out_dict['allergy_recommendations'] = product.allergy_recommendations
    out_dict['reference_unit'] = product.nutrition_facts.reference_quantity.unit
    out_dict['reference_amount'] = product.nutrition_facts.reference_quantity.amount
    out_dict['fiber'] = product.nutrition_facts.nutrients.fiber
    out_dict['salt'] = product.nutrition_facts.nutrients.salt
    out_dict['protein'] = product.nutrition_facts.nutrients.protein
    out_dict['sugars'] = product.nutrition_facts.nutrients.sugars
    out_dict['carbohydrates'] = product.nutrition_facts.nutrients.carbohydrates
    out_dict['saturates'] = product.nutrition_facts.nutrients.saturates
    out_dict['fat'] = product.nutrition_facts.nutrients.fat
    out_dict['kcal'] = product.nutrition_facts.kcal
    out_dict['name_search_standard'] = product.name_search_standard
    return out_dict

  @staticmethod
  def to_product(row):
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
    return Product(
      product_id = row['id'],
      name = row['name'],
      brand_name= row['brand'],
      nutrition_facts=nutrition_facts,
      img_src=row['img_src'],
      category_id= row['category_id'],
      ingredients=row['ingredients'],
      allergy_recommendations=row['allergy_recommendations']
      )