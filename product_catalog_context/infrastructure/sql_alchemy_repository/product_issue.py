from sqlalchemy import select

from product_catalog_context.domain.issues.product_issue import ProductIssue
from product_catalog_context.domain.issues.product_issue_repository import ProductIssueRepository
from product_catalog_context.infrastructure.sql_alchemy_repository.sqlalchemy_repository import BaseSqlAlchemyRepository


class SqlAlchemyProductIssueRepository(ProductIssueRepository, BaseSqlAlchemyRepository):
  def __init__(self, session):
    super().__init__(session)

  async def get_by_id(self, issue_id) -> ProductIssue | None:
    return await self.session.get(ProductIssue, issue_id)

  async def get_pending_issue(self, product_id, reported_field) -> ProductIssue | None:
    query = select(ProductIssue).where(ProductIssue.product_id == product_id, ProductIssue.reported_field == reported_field)
    result = await self._execute(query)
    return result.scalar_one_or_none()

  async def save(self, product_issue: ProductIssue):
    await self._save(product_issue)

  async def delete(self, product_issue: ProductIssue):
    await self.session.delete(product_issue)