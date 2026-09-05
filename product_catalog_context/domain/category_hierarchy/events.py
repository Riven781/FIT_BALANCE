from dataclasses import dataclass
from product_catalog_context.domain.events.event import DomainEvent


@dataclass
class ProductCategoryHierarchyPublished(DomainEvent):
  hierarchy_id: int

@dataclass
class ProductCategoryHierarchyRevertedToDraft(DomainEvent):
  hierarchy_id: int