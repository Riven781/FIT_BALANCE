from product_catalog_context.application.unit_of_work import UnitOfWorkFactory
from product_catalog_context.domain.reports.events import ReportItemMatchedToProductIssue


class AssignReportItemToIssue:
  def __init__(self, unit_of_work_factory: UnitOfWorkFactory):
    self.unit_of_work_factory = unit_of_work_factory

  async def handle(self, event: ReportItemMatchedToProductIssue):
    async with self.unit_of_work_factory() as uow:
      report = await uow.product_reports.get_by_id(event.report_id)
      report.assign_item_to_issue(event.reported_field, event.issue_id)
      await uow.product_reports.save(report)

