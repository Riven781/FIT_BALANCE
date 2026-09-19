from dataclasses import dataclass
from typing import ClassVar
from product_catalog_context.domain.enums.reported_field import ReportedField
from product_catalog_context.domain.messages.message import DomainEvent


@dataclass
class ProductIssueConfirmed(DomainEvent):
  product_id: int
  reported_field: ReportedField
  resolved_value: str | int  
  event_type: ClassVar[str] = 'product_issue_confirmed'
