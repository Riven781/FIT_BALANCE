from product_catalog_context.application.command.product_report import ProductReportCommand
from product_catalog_context.application.unit_of_work import UnitOfWork
from product_catalog_context.domain.issues.product_issue_status import ProductIssueStatus
from product_catalog_context.domain.issues.product_issue import ProductIssue
from product_catalog_context.domain.reports.product_report import ProductReport
from product_catalog_context.domain.reports.product_report_item import ProductReportItem
from product_catalog_context.infrastructure.adapters.access_adapter import AccessAdapter
from product_catalog_context.infrastructure.aiosqlite_repository.product_issue_repository import ProductIssueRepository
from product_catalog_context.infrastructure.aiosqlite_repository.product_report_repository import ProductReportRepository

class ProductReportService:
  def __init__(self, unit_of_work: UnitOfWork, access_adapter: AccessAdapter):
    self.unit_of_work = unit_of_work
    self.access_adapter = access_adapter

  async def create_report(self, product_report_command : ProductReportCommand, user_id): #issue should be created in handler event ReportCreated and id should be add to issue
    async with self.unit_of_work as uow:
      product_report = ProductReport(product_id=product_report_command.product_id, reported_items=[], user_id=user_id)
      for reported_item in product_report_command.reported_items:
        product_report_item = ProductReportItem(reported_field=reported_item.reported_field, proposed_value=reported_item.proposed_value)
        issue = await uow.product_issues.get_pending_issue(product_report_command.product_id, reported_item.reported_field)
        if issue is None:
          new_issue = ProductIssue(product_id=product_report_command.product_id, reported_field=reported_item.reported_field, status=ProductIssueStatus.PENDING)
          await uow.product_issues.save(new_issue)
          product_report_item.assign_to_issue(new_issue.issue_id)
        else:
          product_report_item.assign_to_issue(issue.issue_id)
        product_report.add_reported_item(product_report_item)
      await uow.product_reports.save(product_report)
    return product_report


