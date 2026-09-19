from dataclasses import dataclass
from typing import ClassVar

from product_catalog_context.domain.messages.message import DomainEvent


@dataclass
class ProductCategoryHierarchyPublished(DomainEvent):
  hierarchy_id: int
  event_type: ClassVar[str] = 'product_category_hierarchy_published'

@dataclass
class ProductCategoryHierarchyRevertedToDraft(DomainEvent):
  hierarchy_id: int  
  event_type: ClassVar[str] = 'product_category_hierarchy_reverted_to_draft'
