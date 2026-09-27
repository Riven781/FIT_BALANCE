from product_catalog_context.application.command.product_report import ProductReportCommand
from product_catalog_context.application.errors.errors import ProductNotFoundError, ProductReportExistsForThisVersion
from product_catalog_context.application.unit_of_work import UnitOfWork
from product_catalog_context.domain.issues.product_issue_status import ProductIssueStatus
from product_catalog_context.domain.issues.product_issue import ProductIssue
from product_catalog_context.domain.messages.domain_message_publisher import DomainMessagePublisher
from product_catalog_context.domain.reports.product_report import ProductReport
from product_catalog_context.domain.reports.product_report_item import ProductReportItem
from product_catalog_context.domain.reports.update_report_item_statuses import update_report_item_statuses
from product_catalog_context.infrastructure.adapters.access_adapter import AccessAdapter
from product_catalog_context.infrastructure.aiosqlite_repository.product_issue_repository import ProductIssueRepository
from product_catalog_context.infrastructure.aiosqlite_repository.product_report_repository import ProductReportRepository

class ProductReportService:
  def __init__(self, unit_of_work: UnitOfWork, access_adapter: AccessAdapter, event_publisher: DomainMessagePublisher):
    self.unit_of_work = unit_of_work
    self.access_adapter = access_adapter
    self.event_publisher = event_publisher

  async def create_report(self, product_report_command : ProductReportCommand, user_id):
    async with self.unit_of_work as uow:
      product = await uow.products.get_by_id(product_id=product_report_command.product_id)
      if product is None:
        raise ProductNotFoundError()

      if await uow.product_reports.exists_by_user_and_product_version(user_id, product.version, product.product_id):
        raise ProductReportExistsForThisVersion()
      product_report = ProductReport.create(
        report_id=await uow.product_reports.next_id(),
        product_id=product_report_command.product_id, 
        reported_items=[ProductReportItem(item.reported_field, item.proposed_value, item.old_value) for item in product_report_command.reported_items], 
        user_id=user_id,
        product_version=product.version)

      update_report_item_statuses(product_report, product)

      await uow.product_reports.save(product_report)
      events = product_report.pull_events()
      await self.event_publisher.publish(events, uow_context=uow.context())
  
    return product_report


