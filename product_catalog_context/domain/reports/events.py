from dataclasses import dataclass
from typing import ClassVar

from product_catalog_context.domain.enums.reported_field import ReportedField
from product_catalog_context.domain.messages.message import DomainEvent

@dataclass
class ProductReportCreated(DomainEvent):
  report_id: int
  event_type: ClassVar[str] = 'product_report_created'

@dataclass
class ReportItemMatchedToProductIssue(DomainEvent):
  report_id: int
  issue_id: int
  reported_field: ReportedField
  event_type: ClassVar[str] = 'report_item_matched_to_product_issue'

@dataclass
class ProductReportItemAccepted(DomainEvent):
  report_id: int
  reported_field: ReportedField
  old_value: int
  event_type: ClassVar[str] = 'product_report_item_accepted'


@dataclass
class ReportItemMatchRejected(DomainEvent):
  report_id: int
  reported_field: ReportedField
  event_type: ClassVar[str] = 'report_item_match_rejected'
