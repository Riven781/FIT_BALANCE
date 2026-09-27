from sqlalchemy import insert, literal, select

from product_catalog_context.domain.issues.product_issue import ProductIssue
from product_catalog_context.domain.issues.product_issue_repository import ProductIssueRepository
from product_catalog_context.domain.product.product import Product
from product_catalog_context.infrastructure.sql_alchemy_repository.sqlalchemy_repository import BaseSqlAlchemyRepository
from product_catalog_context.infrastructure.sql_alchemy_repository.mapper import product_report_table, product_report_item_table, product_table, product_issue_table


class SqlAlchemyProductIssueRepository(ProductIssueRepository, BaseSqlAlchemyRepository):
  def __init__(self, session):
    super().__init__(session)

  async def get_by_id(self, issue_id) -> ProductIssue | None:
    return await self.session.get(ProductIssue, issue_id)

  async def get_pending_issue(self, product_id, reported_field) -> ProductIssue | None:
    query = select(ProductIssue).where(ProductIssue.product_id == product_id, ProductIssue.reported_field == reported_field)
    result = await self._execute(query)
    return result.scalar_one_or_none()

  async def get_pending_issue_by_reported_value(self, product_id, reported_field, old_value) -> ProductIssue | None:
    query = select(ProductIssue).where(ProductIssue.product_id == product_id, ProductIssue.reported_field == reported_field, ProductIssue._old_value == old_value)
    result = await self._execute(query)
    return result.scalar_one_or_none()

  async def save(self, product_issue: ProductIssue):
    await self._save(product_issue)

  async def delete(self, product_issue: ProductIssue):
    await self.session.delete(product_issue)

  async def create_if_product_field_unchanged(self, issue: ProductIssue) -> ProductIssue | None:
    product_field = getattr(product_table.c, issue.reported_field)
    #print(f'product_field: {product_field}, issue.old_value: {str(issue.old_value)}  product_id: {issue.product_id}')
    stmt = insert(ProductIssue).from_select(
      ['product_id', 'status', 'reported_field', 'old_value', 'resolved_value', 'resolved_by'],
      select(
        literal(issue.product_id),
        literal(issue.status),
        literal(issue.reported_field),
        literal(issue.old_value),
        literal(issue.resolved_value),
        literal(issue.resolved_by)
      ).select_from(Product)
      .where(
        product_table.c.id == issue.product_id,
        product_field == issue.old_value
      )
    ).returning(ProductIssue)
    result = await self._execute(stmt)
    return result.scalar_one_or_none()