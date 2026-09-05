from re import L

from product_catalog_context.domain.enums.reported_field import ReportedField
from product_catalog_context.domain.events import ProductCategoryChangedInHierarchy, ProductDataChanged
from product_catalog_context.domain.nutrition_facts import NutritionFacts
from product_catalog_context.domain.product_category import ProductCategory
from product_catalog_context.domain.services.text_converter import normalize_for_search

#TODO: delete planned_category_id, current_category_id from domain
class Product:
  PROTECTED_FIELDS = {'product_id', 'name', 'name_search_standard'}

  def __init__(
      self, 
      name, 
      brand_name, 
      nutrition_facts:NutritionFacts, 
      product_id=None, img_src: str=None, ingredients=None, allergy_recommendations=None, name_search_standard=None, created_by=None, category_assignments: dict[int, int] = None):
    self._product_id = product_id
    self.rename(name)
    self.change_brand_name(brand_name)
    self.change_nutrients(nutrition_facts)
    self.img_src = img_src
    self.ingredients = ingredients
    self.allergy_recommendations = allergy_recommendations
    self.created_by = created_by
    self._events = []
    self.category_assignments = category_assignments if category_assignments is not None else {}




  def assign_to_category(self, hierarchy_id, new_category_id, product_editor_id):
    previous_category_id = self.category_assignments.get(hierarchy_id)
    if previous_category_id == new_category_id:
      return
    if new_category_id is None:
      del self.category_assignments[hierarchy_id]
    else:
      self.category_assignments[hierarchy_id] = new_category_id
      self._events.append(ProductCategoryChangedInHierarchy(hierarchy_id=hierarchy_id, product_id=self.product_id, old_category_id=previous_category_id, new_category_id=new_category_id, changed_by=product_editor_id))

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

  def assign_to_planned_category(self, category_id):
    self.planned_category_id = category_id
  

  def change_nutrients(self, nutrition_facts):
    self._nutrition_facts = nutrition_facts

  def generate_search_name(self):
    self.name_search_standard = normalize_for_search(self.name)

  def update_details(self, data: dict, product_editor_id):
    #if self.planned_category_id != data.get('planned_category_id') and data.get('planned_category_id') is not None:
    #  self._events.append(PlannedProductCategoryChanged(product_id=self.product_id, old_category_id=self.planned_category_id, new_category_id=data.get('planned_category_id'), changed_by=product_editor_id))   #generate event PRODUCT_PLANNED_CATEGORY_CHANGED -- sprawdamy czy jest task jesli tak to ktory user zmienił i zmieniamy stan na completed lub cancelled
    changed_fields =[]
    if 'name' in data and data['name'] != self.name:
      changed_fields.append(ReportedField('name'))
      self.rename(data['name'])

    for key, value in data.items():
      if key not in self.PROTECTED_FIELDS and hasattr(self, key):
        setattr(self, key, value)
      if key in [field.value for field in ReportedField]:
        changed_fields.append(ReportedField(key))
    if changed_fields:
      self._events.append(ProductDataChanged(product_id=self.product_id, fields=changed_fields))


  def pull_events(self):
    events = self._events
    self._events = []
    return events

  def resolve_issue(self, reported_field: ReportedField, new_value):
    setattr(self, reported_field.value, new_value)

#normalized_name better




  


    