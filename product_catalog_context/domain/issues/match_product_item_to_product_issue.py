from product_catalog_context.domain.enums.reported_field import ReportedField
from product_catalog_context.domain.issues.product_issue import ProductIssue
from product_catalog_context.domain.reports.events import ReportItemMatchRejected, ReportItemMatchedToProductIssue


def match_product_item_to_product_issue(report_id, reported_field: ReportedField, issue: ProductIssue):
  events = []
  if issue is None:
    events.append(ReportItemMatchRejected)
  else:
    events.append(ReportItemMatchedToProductIssue(report_id, issue.issue_id, reported_field))
  return events