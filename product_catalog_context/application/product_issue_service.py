from product_catalog_context.application.errors.errors import AccessDenied, IssueNotFoundError
from product_catalog_context.application.unit_of_work import UnitOfWork
from product_catalog_context.domain.messages.domain_message_publisher import DomainMessagePublisher
from product_catalog_context.infrastructure.adapters.access_adapter import AccessAdapter
from product_catalog_context.infrastructure.aiosqlite_repository.product_issue_repository import ProductIssueRepository
from product_catalog_context.infrastructure.aiosqlite_repository.product_report_repository import ProductReportRepository


class ProductIssueService:
  def __init__(self, unit_of_work: UnitOfWork, access_adapter: AccessAdapter, event_publisher: DomainMessagePublisher = None):
    self.unit_of_work = unit_of_work
    self.access_adapter = access_adapter
    self.event_publisher = event_publisher

  async def confirm_issue(self, issue_id, resolved_value, moderator_id):#event and update product in handler
    moderator = await self.access_adapter.get_moderator_for(moderator_id)
    if moderator is None:
      raise AccessDenied()
    async with self.unit_of_work as uow:
      product_issue = await uow.product_issues.get_by_id(issue_id)
      if product_issue is None:
        raise IssueNotFoundError()
      product_issue.confirm(resolved_value, moderator_id)
      await uow.product_issues.save(product_issue)

      events = product_issue.pull_events()

    if self.event_publisher:
      await self.event_publisher.publish(events) # not in uow

    return product_issue

  async def reject_issue(self, issue_id, moderator_id):
    moderator = await self.access_adapter.get_moderator_for(moderator_id)
    if moderator is None:
      raise AccessDenied()
    async with self.unit_of_work as uow:
      product_issue = await uow.product_issues.get_by_id(issue_id)
      if product_issue is None:
        raise IssueNotFoundError()
      product_issue.reject(moderator_id)
      await uow.product_issues.save(product_issue)
    return product_issue