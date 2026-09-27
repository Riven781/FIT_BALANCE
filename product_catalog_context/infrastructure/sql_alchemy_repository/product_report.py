from sqlalchemy import exists, select

from product_catalog_context.domain.reports.product_report import ProductReport
from product_catalog_context.domain.reports.product_report_repository import ProductReportRepository
from product_catalog_context.infrastructure.sql_alchemy_repository.sqlalchemy_repository import BaseSqlAlchemyRepository
import sqlalchemy.dialects.sqlite as sqlite
from product_catalog_context.infrastructure.sql_alchemy_repository.mapper import id_seq_table


class SqlAlchemyProductReportRepository(ProductReportRepository, BaseSqlAlchemyRepository):
  def __init__(self, session):
    super().__init__(session)

  async def get_by_id(self, report_id) -> ProductReport | None:
    return await self.session.get(ProductReport, report_id)

  async def exists_by_user_and_product_version(self, user_id, product_version, product_id) -> bool:
    query = select(exists().where(ProductReport.user_id == user_id, ProductReport.product_version == product_version, ProductReport.product_id == product_id))
    result = await self._execute(query)
    return result.scalar_one_or_none()

  async def save(self, product_report: ProductReport):
    await self._save(product_report)

  async def delete(self, product_report: ProductReport):
    await self.session.delete(product_report)

  async def next_id(self):
    query = (
      sqlite.insert(id_seq_table)
      .values(
        name = 'product_report',
        next_value=100
      ).on_conflict_do_update(
        index_elements=[id_seq_table.c.name],
        set_= {
          "next_value" : id_seq_table.c.next_value + 1
        }
      )
      .returning(
        (id_seq_table.c.next_value - 1).label('id')
      )
    )
    result = await self._execute(query)
    return result.scalar_one()