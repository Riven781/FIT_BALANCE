import sqlalchemy
import sqlalchemy.exc

from product_catalog_context.application.ports.message_writer import MessageWriter
from product_catalog_context.application.unit_of_work import UnitOfWork, UnitOfWorkFactory
from sqlalchemy.ext.asyncio import AsyncSession
from product_catalog_context.domain.category_hierarchy.plan_hiearachy_for_publication_saga.plan_hierarchy_for_publication_saga import PlanHierarchyForPublicationSaga
from product_catalog_context.domain.category_hierarchy.plan_hiearachy_for_publication_saga.plan_hierarchy_for_publication_saga_repository import PlanHierarchyForPublicationSagaRepository
from product_catalog_context.domain.category_hierarchy.product_category_hierarchy_repository import ProductCategoryHierarchyRepository
from product_catalog_context.domain.issues.confirmation_saga.product_issue_confirmation_saga_repository import ProductIssueConfirmationSagaRepository
from product_catalog_context.domain.issues.product_issue_repository import ProductIssueRepository
from product_catalog_context.domain.product.product_repository import ProductRepository
from product_catalog_context.domain.reports.product_report_repository import ProductReportRepository
from product_catalog_context.domain.tasks.category_assignment_task_repository import CategoryAssignmentTaskRepository
from product_catalog_context.infrastructure.aiosqlite_repository.errors_mapper import mapped_error
from product_catalog_context.infrastructure.outbox.message_writer import SqlAlchemyOutboxMessageWriter
from product_catalog_context.infrastructure.sql_alchemy_repository.category_assignment_task import SqlAlchemyCategoryAssignmentTaskRepository
from product_catalog_context.infrastructure.sql_alchemy_repository.plan_hierarchy_for_publication_saga_repository import SqlAlchemyPlanHierarchyForPublicationSagaRepository
from product_catalog_context.infrastructure.sql_alchemy_repository.product import SqlAlchemyProductRepository
from product_catalog_context.infrastructure.sql_alchemy_repository.product_category_hierarchy import SqlAlchemyProductCategoryHierarchyRepository
from product_catalog_context.infrastructure.sql_alchemy_repository.product_issue import SqlAlchemyProductIssueRepository
from product_catalog_context.infrastructure.sql_alchemy_repository.product_issue_confirmation_saga_repository import SqlAlchemyProductIssueConfirmationSagaRepository
from product_catalog_context.infrastructure.sql_alchemy_repository.product_report import SqlAlchemyProductReportRepository


class SqlAlchemyUnitOfWork(UnitOfWork):
  def __init__(self, session_factory):
    self.session_factory = session_factory
    self._products = None
    self._product_category_hierarchies = None
    self._category_assignment_tasks = None
    self._product_issues = None
    self._product_reports = None
    self._message_writer = None
    self._product_issues_confirmation_sagas = None
    self._plan_hierarchy_for_publication_sagas = None
    self.session = None


  async def __aenter__(self):
    self.session = self.session_factory()
    self._products = None
    self._product_category_hierarchies = None
    self._category_assignment_tasks = None
    self._product_issues = None
    self._product_reports = None
    self._product_issues_confirmation_sagas = None
    self._plan_hierarchy_for_publication_sagas = None
    self._message_writer = None
    return self

  async def __aexit__(self, exc_type, exc, tb):
    try:
      if exc is not None:
        print(exc)
        await self.rollback()
        if isinstance(exc, sqlalchemy.exc.SQLAlchemyError):
          raise mapped_error(exc) from exc
      else:
        try:
          await self.commit()
        except sqlalchemy.exc.SQLAlchemyError as e:
          await self.rollback()
          raise mapped_error(e) from e
    finally:
      if self.session is not None:
        await self.session.close()
      self.session = None

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

  @property
  def product_issues_confirmation_sagas(self) -> ProductIssueConfirmationSagaRepository:
    if self._product_issues_confirmation_sagas is None:
      self._product_issues_confirmation_sagas = SqlAlchemyProductIssueConfirmationSagaRepository(self.session)
    return self._product_issues_confirmation_sagas

  @property
  def plan_hierarchy_for_publication_sagas(self) -> PlanHierarchyForPublicationSagaRepository:
    if self._plan_hierarchy_for_publication_sagas is None:
      self._plan_hierarchy_for_publication_sagas = SqlAlchemyPlanHierarchyForPublicationSagaRepository(self.session)
    return self._plan_hierarchy_for_publication_sagas
  
  @property
  def message_writer(self) -> MessageWriter:
    if self._message_writer is None:
      self._message_writer = SqlAlchemyOutboxMessageWriter(self.session)
    return self._message_writer
  
  


class SqlAlchemyUnitOfWorkFactory(UnitOfWorkFactory):
  def __init__(self, session_factory):
    self.session_factory = session_factory

  def create(self):
    return SqlAlchemyUnitOfWork(session_factory=self.session_factory)