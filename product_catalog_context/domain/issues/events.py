from dataclasses import dataclass
from typing import ClassVar

from product_catalog_context.domain.enums.reported_field import ReportedField
from product_catalog_context.domain.messages.message import DomainEvent


@dataclass
class ProductIssueConfirmationStarted(DomainEvent):
  issue_id: int
  product_id: int
  resolved_value: int
  old_value: int
  reported_field: ReportedField
  event_type: ClassVar[str] = 'product_issue_confirmation_started'



@dataclass
class ResolvedValueAppliedToProduct(DomainEvent):
  product_id: int
  resolved_value: int
  event_type: ClassVar[str] = 'resolved_value_applied_to_product'

@dataclass
class ProductIssueConfirmed(DomainEvent):
  issue_id: int
  event_type: ClassVar[str] = 'product_issue_confirmed'

@dataclass
class ProductIssueConfirmationCancelledAsObsolete(DomainEvent):
  issue_id: int
  event_type: ClassVar[str] = 'product_issue_confirmation_cancelled_as_obsolete'

@dataclass
class ProductIssueFailed(DomainEvent):
  issue_id: int
  event_type: ClassVar[str] = 'product_issue_failed'

@dataclass
class MessageExecutionFailed(DomainEvent):
  message_name: str
  message_type: str
  error_type: str
  event_type: ClassVar[str] = 'message_execution_failed'

@dataclass
class ProductIssueResetToPending(DomainEvent):
  issue_id: int
  event_type: ClassVar[str] = 'product_issue_reset_to_pending'
