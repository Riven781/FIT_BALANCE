from product_catalog_context.domain.issues.events import ProductIssueConfirmationCancelledAsObsolete, ProductIssueConfirmationStarted, ProductIssueConfirmed, ProductIssueResetToPending
from product_catalog_context.domain.issues.product_issue_status import ProductIssueStatus
from product_catalog_context.domain.enums.reported_field import ReportedField
from product_catalog_context.domain.errors import IssueCanNotBeConfirmed, IssueCanNotBeMarkedAsObsolete, IssueCanNotBeRejected, IssueCanNotBeReset


class ProductIssue:
  def __init__(self, product_id, reported_field: ReportedField, status: ProductIssueStatus=ProductIssueStatus.PENDING, old_value=None, resolved_value = None, issue_id = None, resolved_by=None):
    self.issue_id = issue_id
    self.product_id = product_id
    self.reported_field = reported_field
    self.status = status
    self.resolved_value = resolved_value
    self.resolved_by = resolved_by
    self._old_value = old_value
    self._events = []

  @property
  def old_value(self):
    if self._old_value is None:
      return None
    if self.reported_field == ReportedField.NAME:
      return str(self._old_value)
    if self.reported_field == ReportedField.KCAL:
      return int(self._old_value)
    return float(self._old_value)
  def start_confirmation(self, resolved_value, user_id):
    if self.status != ProductIssueStatus.PENDING:
      raise IssueCanNotBeConfirmed()
    self.resolved_value = resolved_value
    self.status = ProductIssueStatus.CONFIRMATION_PENDING
    self.resolved_by = user_id
    self._events.append(ProductIssueConfirmationStarted(issue_id=self.issue_id, product_id=self.product_id, old_value=self.old_value, resolved_value=resolved_value, reported_field=self.reported_field))

    #self._events.append(ProductIssueConfirmed(product_id=self.product_id, reported_field=self.reported_field, resolved_value=resolved_value))

  def confirm(self, saga_id):
    if self.status == ProductIssueStatus.CONFIRMED:
      return
    
    if self.status != ProductIssueStatus.CONFIRMATION_PENDING:
      raise IssueCanNotBeConfirmed()
    self.status = ProductIssueStatus.CONFIRMED
    self._events.append(ProductIssueConfirmed(issue_id=self.issue_id, saga_id=saga_id))



  def reject(self, user_id):
    if self.status != ProductIssueStatus.PENDING:
      raise IssueCanNotBeRejected()
    self.status = ProductIssueStatus.REJECTED
    self.resolved_by = user_id

  def mark_as_obsolete(self):
    if self.status == ProductIssueStatus.OBSOLETE:
      return
    if self.status != ProductIssueStatus.PENDING:
      raise IssueCanNotBeMarkedAsObsolete()
    self.status = ProductIssueStatus.OBSOLETE

  def cancel_confirmation_as_obsolete(self, saga_id):
    if self.status == ProductIssueStatus.OBSOLETE:
      return
    if self.status != ProductIssueStatus.CONFIRMATION_PENDING:
      raise IssueCanNotBeMarkedAsObsolete()
    self.status = ProductIssueStatus.OBSOLETE
    self._events.append(ProductIssueConfirmationCancelledAsObsolete(issue_id=self.issue_id, saga_id=saga_id))

  def reset_confirmation(self, saga_id):
    if self.status == ProductIssueStatus.PENDING:
      return
    if self.status != ProductIssueStatus.CONFIRMATION_PENDING:
      raise IssueCanNotBeReset()
    self.status = ProductIssueStatus.PENDING
    self._events.append(ProductIssueResetToPending(issue_id=self.issue_id, saga_id=saga_id))


  def pull_events(self):
    events = self._events
    self._events = []
    return events