from dataclasses import dataclass
from typing import ClassVar
from product_catalog_context.domain.enums.reported_field import ReportedField
from product_catalog_context.domain.messages.message import DomainEvent


@dataclass
class ProductCategoryChangedInHierarchy(DomainEvent):
  product_id: int
  hierarchy_id: int
  old_category_id: int
  new_category_id: int
  changed_by: int
  event_type: ClassVar[str] = 'product_category_changed_in_hierarchy'

@dataclass
class ProductDataChanged(DomainEvent):
  product_id: int
  fields: list[ReportedField]
  event_type: ClassVar[str] = 'product_data_changed'

#class ResolvedValueRejectionReason():


@dataclass
class ResolvedValueApplicationRejected(DomainEvent):
  product_id: int
  field: ReportedField
  event_type: ClassVar[str] = 'resolved_value_application_rejected'

@dataclass
class ProductAssignmentCopied(DomainEvent):
  hierarchy_id: int
  event_type: ClassVar[str] = 'product_assignment_copied'

