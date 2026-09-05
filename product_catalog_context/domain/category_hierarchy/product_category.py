from dataclasses import dataclass
from re import fullmatch


class ProductCategory:
  def __init__(self, name : str,   parent_id : int, category_id : int | None = None, source_node_id : int | None = None):
    self.category_id = category_id
    self.name = name
    self.parent_id = parent_id
    self.source_node_id = source_node_id

  def rename(self, name):
    if fullmatch(r's*', name):
      raise ValueError()
    self.name = name

  def change_parent(self, parent_id):
    self.parent_id = parent_id

  def __str__(self):
    return self.category_id
  
  def __repr__(self):
    return str(self.category_id)

class ProductCategoryDraft:
  def __init__(self, name, parent_id, temp_id=None):
    self.name = name
    self.parent_id = parent_id
    self.temp_id = temp_id

class ProductCategoryItem:
  def __init__(self, name : str,   parent_id : int, category_id : int | None = None):
    self.category_id = category_id
    self.name = name
    self.parent_id = parent_id


@dataclass
class ProductCategoryNode:
  category_id : int
  name : str
  parent_id : int