from product_catalog_context.domain.issues.product_issue_status import ProductIssueStatus
from product_catalog_context.domain.reports.report_outcome import ReportOutcome
from product_catalog_context.domain.reports.report_status import ReportStatus
from product_catalog_context.domain.reports.product_report_item import ProductReportItem


class ProductReport:
  def __init__(self,  product_id, reported_items : list[ProductReportItem], user_id = None, report_id = None):
    self.report_id = report_id
    self.reported_items = reported_items
    self.product_id = product_id
    self.user_id = user_id

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
