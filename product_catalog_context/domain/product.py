from re import L

from product_catalog_context.domain.nutrition_facts import NutritionFacts
from product_catalog_context.domain.product_category import ProductCategory
from product_catalog_context.domain.services.text_converter import normalize_for_search


class Product:
  PROTECTED_FIELDS = {'product_id', 'name', 'name_search_standard'}

  def __init__(self, name, brand_name, nutrition_facts:NutritionFacts, category_id, product_id=None, img_src: str=None, ingredients=None, allergy_recommendations=None, name_search_standard=None):
    self._product_id = product_id
    self.rename(name)
    self.change_brand_name(brand_name)
    self.change_nutrients(nutrition_facts)
    self.img_src = img_src
    self.ingredients = ingredients
    self.allergy_recommendations = allergy_recommendations
    self.category_id = category_id

  @property
  def product_id(self):
    return self._product_id
  
  @property
  def name(self) -> str:
    return self._name
  
  def rename(self, new_name : str):
    if not new_name:
      raise ValueError('Product name cannot be empty.')
    self._name = new_name
    self.generate_search_name()

  @property
  def brand_name(self) -> str:
    return self._brand_name

  @brand_name.setter
  def brand_name(self, brand_name):
    self._brand_name = brand_name

  @property
  def nutrition_facts(self):
    return self._nutrition_facts

  @nutrition_facts.setter
  def nutrition_facts(self, nutrition_facts):
    self._nutrition_facts = nutrition_facts
  

  def change_brand_name(self, brand_name: str):
    if not brand_name:
      raise ValueError('Brand name cannot be empty.')
    self._brand_name = brand_name


  

  def change_nutrients(self, nutrition_facts):
    self._nutrition_facts = nutrition_facts

  def generate_search_name(self):
    self.name_search_standard = normalize_for_search(self.name)

  def update_details(self, data: dict):
    if 'name' in data and data['name'] != self.name:
      self.rename(data['name'])

    for key, value in data.items():
      if key not in self.PROTECTED_FIELDS and hasattr(self, key):
        setattr(self, key, value)

#normalized_name better




  


    