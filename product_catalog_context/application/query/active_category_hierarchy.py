from dataclasses import dataclass


@dataclass
class CategoryHierarchyNode:
  id: int
  name: str
  subcategories: list['CategoryHierarchyNode']

@dataclass
class ActiveCategoryHierarchy:
  categories: list[CategoryHierarchyNode]