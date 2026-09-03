from product_catalog_context.domain.events import ProductDataChanged
from product_catalog_context.infrastructure.aiosqlite_repository.product_issue_repository import ProductIssueRepository

class ProductDataChangedHandler:
  def __init__(self, product_issue_repository: ProductIssueRepository):
    self.product_issue_repository = product_issue_repository

  async def handle(self, event: ProductDataChanged):
    for field in event.fields:
      issue = await self.product_issue_repository.get_pending_issue(product_id=event.product_id, reported_field=field)
      if issue is not None:
        issue.mark_as_obsolete()
      self.product_issue_repository.update(issue)