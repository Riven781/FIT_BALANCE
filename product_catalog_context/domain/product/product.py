from dataclasses import fields
from re import L

from product_catalog_context.domain.enums.reported_field import ReportedField
from product_catalog_context.domain.errors import ProductCategoryAssignmentConflict
from product_catalog_context.domain.product.events import ProductCategoryChangedInHierarchy, ProductDataChanged
from product_catalog_context.domain.product.nutrition_facts import Nutrients, NutritionFacts
from product_catalog_context.domain.category_hierarchy.product_category import ProductCategory
from product_catalog_context.domain.product.product_assignment import CategoryAssignment
from product_catalog_context.domain.product.product_details import ProductDetails
from product_catalog_context.domain.repository.errors import ConcurrentModification
from product_catalog_context.domain.services.text_converter import normalize_for_search

class Product:
  PROTECTED_FIELDS = {'product_id', 'name', 'name_search_standard'}

  def __init__(
      self, 
      name, 
      brand_name, 
      nutrition_facts:NutritionFacts, 
      product_id=None, img_src: str=None, ingredients=None, allergy_recommendations=None, name_search_standard=None, created_by=None, category_assignments: dict[int, CategoryAssignment] = None):
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




  def assign_to_category(self, hierarchy_id, new_category_id, product_editor_id, expected_version):
    previous_category_assignment = self.category_assignments.get(hierarchy_id)
    if previous_category_assignment is not None:
      print(f'category_id: {new_category_id} version: {previous_category_assignment.version} expected: {expected_version}')
      if previous_category_assignment.version != expected_version:
        raise ProductCategoryAssignmentConflict()
    previous_category_id = previous_category_assignment.category_id if previous_category_assignment else None
    if previous_category_id == new_category_id:
      return
    if new_category_id is None:
      del self.category_assignments[hierarchy_id]
    else:
      self.category_assignments[hierarchy_id] = CategoryAssignment(category_id=new_category_id, assigned_by=product_editor_id, version=previous_category_assignment.version if previous_category_assignment else None) 
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

  def _get_changed_nutrients(self, old: Nutrients, new: Nutrients):
    return [ReportedField(field.name) for field in fields(Nutrients) if getattr(old, field.name) != getattr(new, field.name)]

  def get_changed_fields(self, details: ProductDetails):
    changed_fields = []
    if details.name != self.name:
      changed_fields.append(ReportedField('name'))
    if details.nutrition_facts.kcal != self.nutrition_facts.kcal:
      changed_fields.append(ReportedField('kcal'))
    changed_fields.extend(self._get_changed_nutrients(self.nutrition_facts.nutrients, details.nutrition_facts.nutrients))
    return changed_fields

  def update_details(self, details: ProductDetails, product_editor_id):
    changed_fields = self.get_changed_fields(details)
    if self.name != details.name:
      self.rename(details.name)
    if self.brand_name != details.brand_name:
      self.change_brand_name(details.brand_name)
    if self.nutrition_facts != details.nutrition_facts:
      self.change_nutrients(details.nutrition_facts)
    if self.img_src != details.img_src:
      self.img_src = details.img_src
    if self.ingredients != details.ingredients:
      self.ingredients = details.ingredients
    if self.allergy_recommendations != details.allergy_recommendations:
      self.allergy_recommendations = details.allergy_recommendations

    if changed_fields:
      self._events.append(ProductDataChanged(product_id=self.product_id, fields=changed_fields))


  def pull_events(self):
    events = self._events
    self._events = []
    return events

  def resolve_issue(self, reported_field: ReportedField, new_value):#but str is given as reported field so without .value
    if reported_field == ReportedField.NAME:
      self.rename(new_value)
    elif reported_field == ReportedField.KCAL:
      self._nutrition_facts = self.nutrition_facts.with_updates(kcal=new_value)
    else:
      self._nutrition_facts = self.nutrition_facts.with_updates(nutrients={reported_field:new_value})


#normalized_name better




  


    