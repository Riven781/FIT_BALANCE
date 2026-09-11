from abc import ABC, abstractmethod

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