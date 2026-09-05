from dataclasses import dataclass
from product_catalog_context.domain.events.event import DomainEvent
from product_catalog_context.domain.enums.reported_field import ReportedField


@dataclass
class ProductCategoryChangedInHierarchy(DomainEvent):
  product_id: int
  hierarchy_id: int
  old_category_id: int
  new_category_id: int
  changed_by: int

@dataclass
class ProductDataChanged(DomainEvent):
  product_id: int
  fields: list[ReportedField]

