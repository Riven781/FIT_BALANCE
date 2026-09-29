from dataclasses import dataclass
from typing import ClassVar

from product_catalog_context.domain.enums.reported_field import ReportedField
from product_catalog_context.domain.messages.message import DomainCommand

@dataclass
class ProductIssueConfirmationCommand(DomainCommand):
  saga_type: ClassVar[str] = 'product_issue_confirmation_saga'

@dataclass
class ApplyResolvedValueToProduct(ProductIssueConfirmationCommand):
  product_id: int
  resolved_value: int
  reported_field: ReportedField
  old_value: int
  command_type: ClassVar[str] = 'apply_resolved_value_to_product'


@dataclass
class ConfirmProductIssue(ProductIssueConfirmationCommand):
  issue_id: int
  command_type: ClassVar[str] = 'confirm_product_issue'


@dataclass
class CancelProductIssueConfirmation(ProductIssueConfirmationCommand):
  issue_id: int
  command_type: ClassVar[str] = 'cancel_product_issue_confirmation'

@dataclass
class ResetProductIssueToPending(ProductIssueConfirmationCommand):
  issue_id: int
  command_type: ClassVar[str] = 'reset_product_issue_to_pending'

