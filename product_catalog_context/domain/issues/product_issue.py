from product_catalog_context.domain.enums.product_issue_status import ProductIssueStatus
from product_catalog_context.domain.enums.reported_field import ReportedField
from product_catalog_context.domain.errors import IssueCanNotBeConfirmed, IssueCanNotBeMarkedAsObsolete, IssueCanNotBeRejected


class ProductIssue:
  def __init__(self, product_id, reported_field: ReportedField, status: ProductIssueStatus, resolved_value = None, issue_id = None):
    self.issue_id = issue_id
    self.product_id = product_id
    self.reported_field = reported_field
    self.status = status
    self.resolved_value = resolved_value

  def confirm(self, resolved_value):
    if self.status != ProductIssueStatus.PENDING:
      raise IssueCanNotBeConfirmed()
    self.resolved_value = resolved_value
    self.status = ProductIssueStatus.CONFIRMED

  def reject(self):
    if self.status != ProductIssueStatus.PENDING:
      raise IssueCanNotBeRejected()
    self.status = ProductIssueStatus.REJECTED

  def mark_as_obsolete(self):
    if self.status != ProductIssueStatus.PENDING:
      raise IssueCanNotBeMarkedAsObsolete()
    self.status = ProductIssueStatus.OBSOLETE


  