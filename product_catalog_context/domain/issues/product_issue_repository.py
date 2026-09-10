from abc import ABC, abstractmethod

from product_catalog_context.domain.issues.product_issue import ProductIssue


class ProductIssueRepository(ABC):
  @abstractmethod
  async def get_by_id(self, issue_id) -> ProductIssue | None:
    pass

  @abstractmethod
  async def get_pending_issue(self, product_id, reported_field):
    pass

  @abstractmethod
  async def save(self, product_issue: ProductIssue):
    pass

  @abstractmethod
  async def delete(self, product_issue: ProductIssue):
    pass