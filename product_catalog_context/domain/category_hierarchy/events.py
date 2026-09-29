from dataclasses import dataclass
from typing import ClassVar

from product_catalog_context.domain.messages.message import DomainEvent


@dataclass
class ProductCategoryHierarchyPublished(DomainEvent):
  hierarchy_id: int
  event_type: ClassVar[str] = 'product_category_hierarchy_published'

@dataclass
class HierarchyRevertedToDraft(DomainEvent):
  hierarchy_id: int  
  event_type: ClassVar[str] = 'hierarchy_reverted_to_draft'

@dataclass
class HierarchyPlannedForPublication(DomainEvent):
  hierarchy_id: int  
  event_type: ClassVar[str] = 'hierarchy_planned_for_publication'

@dataclass
class PlanningForPublicationStarted(DomainEvent):
  hierarchy_id: int  
  event_type: ClassVar[str] = 'planning_for_publication_started'

@dataclass
class HierarchyRolledBackToDraft(DomainEvent):
  hierarchy_id: int  
  event_type: ClassVar[str] = 'hierarchy_rolled_back_to_draft'