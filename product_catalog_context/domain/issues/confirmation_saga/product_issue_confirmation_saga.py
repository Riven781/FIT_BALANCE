from functools import singledispatchmethod

from product_catalog_context.domain.issues.confirmation_saga.commands import ApplyResolvedValueToProduct, CancelProductIssueConfirmation, ConfirmProductIssue, ResetProductIssueToPending
from product_catalog_context.domain.issues.confirmation_saga.saga_status import ProductIssueConfirmationSagaStatus


class ProductIssueConfirmationSaga:
  def __init__(self, issue_id:int, status = ProductIssueConfirmationSagaStatus.STARTED,  saga_id=None):
    self.saga_id = saga_id
    self.issue_id = issue_id
    self.status = status
    self._commands = []

  def start(self, product_id, resolved_value, old_value, reported_field):
    if self.status == ProductIssueConfirmationSagaStatus.STARTED:
      self._commands.append(ApplyResolvedValueToProduct(product_id=product_id, reported_field=reported_field, resolved_value=resolved_value, old_value=old_value, saga_id=self.saga_id))
      self.status=ProductIssueConfirmationSagaStatus.PRODUCT_UPDATE_PENDING

  def cancel(self):
    if self.status == ProductIssueConfirmationSagaStatus.PRODUCT_UPDATE_PENDING:
      self._commands.append(CancelProductIssueConfirmation(issue_id=self.issue_id, saga_id=self.saga_id))
      self.status=ProductIssueConfirmationSagaStatus.CANCELLATION_PENDING

  def confirm(self):
    if self.status == ProductIssueConfirmationSagaStatus.PRODUCT_UPDATE_PENDING:
      self._commands.append(ConfirmProductIssue(issue_id=self.issue_id, saga_id=self.saga_id))
      self.status=ProductIssueConfirmationSagaStatus.ISSUE_CONFIRMATION_PENDING

  def obsolete(self):
    if self.status == ProductIssueConfirmationSagaStatus.CANCELLATION_PENDING:
      self.status = ProductIssueConfirmationSagaStatus.OBSOLETE

  def complete(self):
    if self.status == ProductIssueConfirmationSagaStatus.ISSUE_CONFIRMATION_PENDING:
      self.status=ProductIssueConfirmationSagaStatus.COMPLETED

  def reset_completed(self):
    if self.status == ProductIssueConfirmationSagaStatus.ISSUE_RESET_PENDING:
      self.status = ProductIssueConfirmationSagaStatus.FAILED

  def handle_message_failure(self, message_name):
    if message_name == ApplyResolvedValueToProduct.command_type and self.status == ProductIssueConfirmationSagaStatus.PRODUCT_UPDATE_PENDING:
      self._commands.append(ResetProductIssueToPending(issue_id=self.issue_id, saga_id=self.saga_id))
      self.status = ProductIssueConfirmationSagaStatus.ISSUE_RESET_PENDING
  
   

  def pull_commands(self):
    commands = self._commands
    self._commands = []
    return commands