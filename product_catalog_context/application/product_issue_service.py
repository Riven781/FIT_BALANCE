from product_catalog_context.application.errors.errors import IssueNotFoundError
from product_catalog_context.infrastructure.aiosqlite_repository.product_issue_repository import ProductIssueRepository
from product_catalog_context.infrastructure.aiosqlite_repository.product_report_repository import ProductReportRepository


class ProductIssueService:
  def __init__(self, product_issue_repository: ProductIssueRepository):
    self.product_issue_repository = product_issue_repository

  async def confirm_issue(self, issue_id, resolved_value):#event and update product in handler
    product_issue = await self.product_issue_repository.get_by_id(issue_id)
    if product_issue is None:
      raise IssueNotFoundError()
    product_issue.confirm(resolved_value)
    await self.product_issue_repository.update(product_issue.issue_id, product_issue)
    return product_issue

  async def reject_issue(self, issue_id):
    product_issue = await self.product_issue_repository.get_by_id(issue_id)
    if product_issue is None:
      raise IssueNotFoundError()
    product_issue.reject()
    await self.product_issue_repository.update(product_issue.issue_id, product_issue)
    return product_issue