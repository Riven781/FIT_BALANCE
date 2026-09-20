from abc import ABC, abstractmethod

from product_catalog_context.application.ports.message_writer import MessageWriter
from product_catalog_context.domain.category_hierarchy.product_category_hierarchy_repository import ProductCategoryHierarchyRepository
from product_catalog_context.domain.issues.product_issue_repository import ProductIssueRepository
from product_catalog_context.domain.product.product_repository import ProductRepository
from product_catalog_context.domain.reports.product_report_repository import ProductReportRepository
from product_catalog_context.domain.tasks.category_assignment_task_repository import CategoryAssignmentTaskRepository


class UnitOfWork(ABC):

  @abstractmethod
  async def __aenter__(self) -> "UnitOfWork":
    pass

  @abstractmethod
  async def __aexit__(self, exc_type, exc, tb):
    pass

  async def commit(self) -> None:
    pass

  async def rollback(self) -> None:
    pass



  @property
  def products(self) -> ProductRepository:
    pass

  @property
  def product_category_hierarchies(self) -> ProductCategoryHierarchyRepository:
    pass

  @property
  def category_assignment_tasks(self) -> CategoryAssignmentTaskRepository:
    pass

  @property
  def product_issues(self) -> ProductIssueRepository:
    pass

  @property
  def product_reports(self) -> ProductReportRepository:
    pass

  @property
  def message_writer(self) -> MessageWriter:
    pass

  def context(self) -> "UnitOfWorkContext":
    return UnitOfWorkContext(self)


class UnitOfWorkContext():
  def __init__(self, uow: UnitOfWork):
    self.uow = uow
  @property
  def session(self):
    return self.uow.session

  @property
  def products(self) -> ProductRepository:
    return self.uow.products

  @property
  def product_category_hierarchies(self) -> ProductCategoryHierarchyRepository:
    return self.uow.product_category_hierarchies

  @property
  def category_assignment_tasks(self) -> CategoryAssignmentTaskRepository:
    return self.uow.category_assignment_tasks

  @property
  def product_issues(self) -> ProductIssueRepository:
    return self.uow.product_issues

  @property
  def product_reports(self) -> ProductReportRepository:
    return self.uow.product_reports

  @property
  def message_writer(self) -> MessageWriter:
    return self.uow.message_writer


class UnitOfWorkFactory(ABC):

  @abstractmethod
  def create(self) -> UnitOfWork:
    pass

  def __call__(self) -> UnitOfWork:
    return self.create()