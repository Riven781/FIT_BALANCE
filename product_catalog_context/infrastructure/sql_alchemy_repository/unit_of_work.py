import sqlalchemy
import sqlalchemy.exc

from product_catalog_context.application.unit_of_work import UnitOfWork
from sqlalchemy.ext.asyncio import AsyncSession
from product_catalog_context.domain.category_hierarchy.product_category_hierarchy_repository import ProductCategoryHierarchyRepository
from product_catalog_context.domain.issues.product_issue_repository import ProductIssueRepository
from product_catalog_context.domain.product.product_repository import ProductRepository
from product_catalog_context.domain.reports.product_report_repository import ProductReportRepository
from product_catalog_context.domain.tasks.category_assignment_task_repository import CategoryAssignmentTaskRepository
from product_catalog_context.infrastructure.aiosqlite_repository.errors_mapper import mapped_error
from product_catalog_context.infrastructure.sql_alchemy_repository.category_assignment_task import SqlAlchemyCategoryAssignmentTaskRepository
from product_catalog_context.infrastructure.sql_alchemy_repository.product import SqlAlchemyProductRepository
from product_catalog_context.infrastructure.sql_alchemy_repository.product_category_hierarchy import SqlAlchemyProductCategoryHierarchyRepository
from product_catalog_context.infrastructure.sql_alchemy_repository.product_issue import SqlAlchemyProductIssueRepository
from product_catalog_context.infrastructure.sql_alchemy_repository.product_report import SqlAlchemyProductReportRepository


class SqlAlchemyUnitOfWork(UnitOfWork):
  def __init__(self, session: AsyncSession):
    self.session = session
    self._products = None
    self._product_category_hierarchies = None
    self._category_assignment_tasks = None
    self._product_issues = None
    self._product_reports = None


  async def __aenter__(self):
    return self

  async def __aexit__(self, exc_type, exc, tb):
    if exc is not None:
      await self.rollback()
      if isinstance(exc, sqlalchemy.exc.SQLAlchemyError):
        raise mapped_error(exc) from exc
    else:
      try:
        await self.commit()
      except sqlalchemy.exc.SQLAlchemyError as e:
        await self.rollback()
        raise mapped_error(e) from e

  async def commit(self):
    await self.session.commit()

  async def rollback(self):
    await self.session.rollback()

  @property
  def products(self) -> ProductRepository:
    if self._products is None:
      self._products = SqlAlchemyProductRepository(self.session)
    return self._products

  @property
  def product_category_hierarchies(self) -> ProductCategoryHierarchyRepository:
    if self._product_category_hierarchies is None:
      self._product_category_hierarchies = SqlAlchemyProductCategoryHierarchyRepository(self.session)
    return self._product_category_hierarchies

  @property
  def category_assignment_tasks(self) -> CategoryAssignmentTaskRepository:
    if self._category_assignment_tasks is None:
      self._category_assignment_tasks = SqlAlchemyCategoryAssignmentTaskRepository(self.session)
    return self._category_assignment_tasks

  @property
  def product_issues(self) -> ProductIssueRepository:
    if self._product_issues is None:
      self._product_issues = SqlAlchemyProductIssueRepository(self.session)
    return self._product_issues

  @property
  def product_reports(self) -> ProductReportRepository:
    if self._product_reports is None:
      self._product_reports = SqlAlchemyProductReportRepository(self.session)
    return self._product_reports