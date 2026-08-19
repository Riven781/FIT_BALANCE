from product_catalog_context.domain.enums.product_report_item_status import ProductReportItemStatus
from product_catalog_context.domain.enums.proposed_value_outcome import ProposedValueOutcome
from product_catalog_context.domain.enums.reported_field import ReportedField


class ProductReportItem:
  def __init__(self, reported_field : ReportedField, proposed_value, issue_id = None):
    self.reported_item = reported_field
    self.proposed_value = proposed_value
    self.issue_id = issue_id

  def assign_to_issue(self, issue_id):
    self.issue_id = issue_id
