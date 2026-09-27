from product_catalog_context.domain.reports.product_report_item_status import ProductReportItemStatus
from product_catalog_context.domain.reports.proposed_value_outcome import ProposedValueOutcome
from product_catalog_context.domain.enums.reported_field import ReportedField


class ProductReportItem:
  def __init__(self, reported_field : ReportedField, proposed_value= None, old_value=None, issue_id = None, status: ProductReportItemStatus=None):
    self.reported_field = reported_field
    self.proposed_value = proposed_value
    self.issue_id = issue_id
    self.status = status
    self.old_value = old_value

  def assign_to_issue(self, issue_id):
    self.issue_id = issue_id

  def accept(self):
    self.status = ProductReportItemStatus.ACCEPTED

  def mark_as_outdated(self):
    self.status = ProductReportItemStatus.OUTDATED
