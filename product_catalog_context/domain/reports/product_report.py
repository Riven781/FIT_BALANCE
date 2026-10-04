from product_catalog_context.domain.enums.reported_field import ReportedField
from product_catalog_context.domain.errors import FieldDoesNotExistInReportItems
from product_catalog_context.domain.issues.product_issue_status import ProductIssueStatus
from product_catalog_context.domain.reports.events import ProductReportCreated, ProductReportItemAccepted, ReportItemMatchedToProductIssue
from product_catalog_context.domain.reports.product_report_item_status import ProductReportItemStatus
from product_catalog_context.domain.reports.report_outcome import ReportOutcome
from product_catalog_context.domain.reports.report_status import ReportStatus
from product_catalog_context.domain.reports.product_report_item import ProductReportItem


class ProductReport:
  def __init__(self,  product_id, reported_items : list[ProductReportItem], product_version=1, user_id = None, report_id = None):
    self.report_id = report_id
    self.reported_items = reported_items
    self.product_id = product_id
    self.user_id = user_id
    self.product_version = product_version
    self._events = []

  @classmethod
  def create(cls, product_id, reported_items : list[ProductReportItem], product_version, user_id = None, report_id = None):
    report = cls(product_id, reported_items, product_version, user_id, report_id)
    #report._events.append(ProductReportCreated(report_id=report_id))
    return report

  def evaluate_status(self,  reported_field: ReportedField, product_value):
    item = next((item for item in self.reported_items if item.reported_field == reported_field), None)
    #print(f'REPORTED_FIELD: {reported_field }{type(item.old_value)} - {item.old_value} vs {type(product_value)} - {product_value} : str - {str(product_value)}')
    if str(item.old_value) == str(product_value):
      item.accept()
      self._events.append(ProductReportItemAccepted(self.report_id, reported_field, item.old_value))
    else:
      item.mark_as_outdated()

  def assign_item_to_issue(self, reported_field: ReportedField, issue_id):
    item = self.get_report_item(reported_field)
    item.assign_to_issue(issue_id)

  def accept_report_item(self, reported_field: ReportedField):
    item = next((item for item in self.reported_items if item.reported_field == reported_field), None)
    if item is None:
      raise FieldDoesNotExistInReportItems()
    item.accept()

  def mark_report_item_as_outdated(self, reported_field: ReportedField):
    item = next((item for item in self.reported_items if item.reported_field == reported_field), None)
    if item is None:
      raise FieldDoesNotExistInReportItems()
    item.mark_as_outdated()

  def pull_events(self):
    events = self._events
    self._events = []
    return events

  def get_reported_fields(self):
    return [item.reported_field for item in self.reported_items]

  def get_report_item(self, reported_field):
    item = next((item for item in self.reported_items if item.reported_field == reported_field), None)
    if item is None:
      raise FieldDoesNotExistInReportItems()
    return item

  def is_issue_assigned(self, reported_field):
    item = self.get_report_item(reported_field)
    return item.issue_id is not None


  def get_accepted_reported_fields(self):
    return [item.reported_field for item in self.reported_items if item.status == ProductReportItemStatus.ACCEPTED] 

  def issue_ids(self):
    return [reported_item.issue_id for reported_item in self.reported_items]

  def add_reported_item(self, reported_item):
    self.reported_items.append(reported_item)

  def calculate_status(self, issue_statuses) -> ReportStatus:
    if all(status in [ProductIssueStatus.CONFIRMED, ProductIssueStatus.REJECTED, ProductIssueStatus.OBSOLETE] for status in issue_statuses):
      return ReportStatus.REVIEWED
    if any(status in [ProductIssueStatus.CONFIRMED, ProductIssueStatus.REJECTED, ProductIssueStatus.OBSOLETE] for status in issue_statuses):
        return ReportStatus.PARTIALLY_REVIEWED
    return ReportStatus.PENDING

  def calculate_outcome(self, issue_statuses):
    if self.calculate_status(issue_statuses) == ReportStatus.PENDING:
      return ReportOutcome.IN_REVIEW
    if all(status == ProductIssueStatus.OBSOLETE for status in issue_statuses):
      return ReportOutcome.OBSOLETE
    if all(status in [ProductIssueStatus.CONFIRMED, ProductIssueStatus.OBSOLETE] for status in issue_statuses):
      return ReportOutcome.FULLY_CONFIRMED
    if any(status == ProductIssueStatus.CONFIRMED for status in issue_statuses):
      return ReportOutcome.PARTIALLY_CONFIRMED
    return ReportOutcome.REJECTED
