from product_catalog_context.application.errors.errors import AccessDenied, IssueNotFoundError
from product_catalog_context.infrastructure.adapters.access_adapter import AccessAdapter
from product_catalog_context.infrastructure.aiosqlite_repository.product_issue_repository import ProductIssueRepository
from product_catalog_context.infrastructure.aiosqlite_repository.product_report_repository import ProductReportRepository


class ProductIssueService:
  def __init__(self, product_issue_repository: ProductIssueRepository, access_adapter: AccessAdapter):
    self.product_issue_repository = product_issue_repository
    self.access_adapter = access_adapter

  async def confirm_issue(self, issue_id, resolved_value, moderator_id):#event and update product in handler
    moderator = await self.access_adapter.get_moderator_for(moderator_id)
    if moderator is None:
      raise AccessDenied()
    product_issue = await self.product_issue_repository.get_by_id(issue_id)
    if product_issue is None:
      raise IssueNotFoundError()
    product_issue.confirm(resolved_value, moderator_id)
    await self.product_issue_repository.update(product_issue.issue_id, product_issue)
    return product_issue

  async def reject_issue(self, issue_id, moderator_id):
    moderator = await self.access_adapter.get_moderator_for(moderator_id)
    if moderator is None:
      raise AccessDenied()
    product_issue = await self.product_issue_repository.get_by_id(issue_id)
    if product_issue is None:
      raise IssueNotFoundError()
    product_issue.reject(moderator_id)
    await self.product_issue_repository.update(product_issue.issue_id, product_issue)
    return product_issue