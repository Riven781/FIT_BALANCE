from product_catalog_context.application.command.product_report import ProductReportCommand
from product_catalog_context.domain.issues.product_issue_status import ProductIssueStatus
from product_catalog_context.domain.issues.product_issue import ProductIssue
from product_catalog_context.domain.reports.product_report import ProductReport
from product_catalog_context.domain.reports.product_report_item import ProductReportItem
from product_catalog_context.infrastructure.adapters.access_adapter import AccessAdapter
from product_catalog_context.infrastructure.aiosqlite_repository.product_issue_repository import ProductIssueRepository
from product_catalog_context.infrastructure.aiosqlite_repository.product_report_repository import ProductReportRepository

class ProductReportService:
  def __init__(self, product_report_repository: ProductReportRepository, product_issue_repository: ProductIssueRepository, access_adapter: AccessAdapter):
    self.product_report_repository = product_report_repository
    self.product_issue_repository = product_issue_repository
    self.access_adapter = access_adapter

  async def create_report(self, product_report_command : ProductReportCommand, user_id): #issue should be created in handler event ReportCreated and id should be add to issue
    product_report = ProductReport(product_id=product_report_command.product_id, reported_items=[], user_id=user_id)
    for reported_item in product_report_command.reported_items:
      product_report_item = ProductReportItem(reported_field=reported_item.reported_field, proposed_value=reported_item.proposed_value)
      issue = await self.product_issue_repository.get_pending_issue(product_report_command.product_id, reported_item.reported_field)
      if issue is None:
        new_issue = ProductIssue(product_id=product_report_command.product_id, reported_field=reported_item.reported_field, status=ProductIssueStatus.PENDING)
        new_issue_id = await self.product_issue_repository.insert(new_issue)
        product_report_item.assign_to_issue(new_issue_id)
      else:
        product_report_item.assign_to_issue(issue.issue_id)
      product_report.add_reported_item(product_report_item)
    await self.product_report_repository.insert(product_report)
    return product_report


