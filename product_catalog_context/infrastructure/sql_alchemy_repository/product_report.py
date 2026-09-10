from product_catalog_context.domain.reports.product_report import ProductReport
from product_catalog_context.domain.reports.product_report_repository import ProductReportRepository
from product_catalog_context.infrastructure.sql_alchemy_repository.sqlalchemy_repository import BaseSqlAlchemyRepository


class SqlAlchemyProductReport(ProductReportRepository, BaseSqlAlchemyRepository):
  def __init__(self, session):
    super().__init__(session)

  async def get_by_id(self, report_id) -> ProductReport | None:
    return await self.session.get(ProductReport, report_id)

  async def save(self, product_report: ProductReport):
    await self._save(product_report)

  async def delete(self, product_report: ProductReport):
    await self.session.delete(product_report)