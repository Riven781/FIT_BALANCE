from dataclasses import dataclass

@dataclass(frozen=True)
class ProductCategoryDTO:
  category_id: int
  name: str
  parent_id: int | None
  source_node_id: int | None

@dataclass(frozen=True)
class ProductCategoryDraftDTO:
  name: str
  parent_id: int | None
  temp_id: int

@dataclass(frozen=True)
class EditHierarchyCommand:
  hierarchy_id: int
  existing_categories: list[ProductCategoryDTO]
  draft_categories: list[ProductCategoryDraftDTO]
  catalog_manager_id: int