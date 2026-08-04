from product_catalog_context.domain.enums.product_report_item_status import ProductReportItemStatus
from product_catalog_context.domain.enums.proposed_value_outcome import ProposedValueOutcome
from product_catalog_context.domain.enums.reported_item import ReportedItem


class ProductReportItem:
  def __init__(self, reported_item : ReportedItem, proposed_value, status=ProductReportItemStatus.PENDING, proposed_value_outcome=None):
    self.reported_item = reported_item
    self.proposed_value = proposed_value
    self.status = status
    self.proposed_value_outcome = proposed_value_outcome
  
  def confirm(self, value):
    if self.status != ProductReportItemStatus.PENDING:
      raise ValueError()
    self.status = ProductReportItemStatus.CONFIRMED
    if self.proposed_value is None:
      self.proposed_value_outcome = ProposedValueOutcome.NOT_PROVIDED
    else:
      if self.proposed_value == value:
        self.proposed_value = ProposedValueOutcome.CORRECT
      else:
        self.proposed_value = ProposedValueOutcome.INCORRECT
  
  def reject(self):
    if self.status != ProductReportItemStatus.PENDING:
      raise ValueError()
    self.status = ProductReportItemStatus.REJECTED

  def mark_as_obsolete(self):
    if self.status != ProductReportItemStatus.PENDING:
      raise ValueError()
    self.status = ProductReportItemStatus.OBSOLETE


  


    