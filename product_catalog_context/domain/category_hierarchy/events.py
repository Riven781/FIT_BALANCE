from dataclasses import dataclass


@dataclass
class ProductCategoryHierarchyPublished:
  hierarchy_id: int

@dataclass
class ProductCategoryHierarchyRevertedToDraft:
  hierarchy_id: int