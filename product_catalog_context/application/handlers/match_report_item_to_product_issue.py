from product_catalog_context.application.errors.errors import ProductReportDoesNotExist
from product_catalog_context.application.unit_of_work import UnitOfWorkFactory
from product_catalog_context.domain.issues.match_product_item_to_product_issue import match_product_item_to_product_issue
from product_catalog_context.domain.issues.product_issue import ProductIssue
from product_catalog_context.domain.issues.product_issue_status import ProductIssueStatus
from product_catalog_context.domain.messages.domain_message_publisher import DomainMessagePublisher
from product_catalog_context.domain.reports.events import ProductReportCreated, ProductReportItemAccepted, ReportItemMatchRejected


class MatchReportItemToProductIssue:
  def __init__(self, unit_of_work_factory: UnitOfWorkFactory, publisher: DomainMessagePublisher):
    self.unit_of_work_factory = unit_of_work_factory
    self.publisher = publisher

  async def handle(self, event: ProductReportItemAccepted):
    async with self.unit_of_work_factory() as uow:
      report = await uow.product_reports.get_by_id(event.report_id)
      if report is None:
        raise ProductReportDoesNotExist()
      if report.is_issue_assigned(event.reported_field):
        return
      issue = await uow.product_issues.get_pending_issue_by_reported_value(report.product_id, event.reported_field, event.old_value)
      if issue is None:
        issue = await uow.product_issues.create_if_product_field_unchanged(
          ProductIssue(product_id=report.product_id, reported_field=event.reported_field, status=ProductIssueStatus.PENDING, old_value=event.old_value)
        )
      events = match_product_item_to_product_issue(report.report_id, event.reported_field, issue)
      await self.publisher.publish(events, uow_context=uow.context())
