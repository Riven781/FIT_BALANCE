from enum import StrEnum


class ProductCategoryHierarchyStatus(StrEnum):
  ACTIVE = 'ACTIVE'
  PLANNED_FOR_PUBLICATION = 'PLANNED_FOR_PUBLICATION'
  DRAFT = 'DRAFT'