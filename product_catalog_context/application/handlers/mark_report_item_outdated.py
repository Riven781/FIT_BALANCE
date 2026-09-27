from product_catalog_context.application.unit_of_work import UnitOfWorkFactory
from product_catalog_context.domain.reports.events import ReportItemMatchRejected


class MarkReportItemOutdated:
  def __init__(self, unit_of_work_factory: UnitOfWorkFactory):
    self.unit_of_work_factory = unit_of_work_factory

  async def handle(self, event: ReportItemMatchRejected):
    async with self.unit_of_work_factory() as uow:
      report = await uow.product_reports.get_by_id(event.report_id)
      report.mark_report_item_as_outdated(event.reported_field)
      await uow.product_reports.save(report)