from product_catalog_context.application.unit_of_work import UnitOfWork, UnitOfWorkFactory
from product_catalog_context.domain.errors import IssueCanNotBeMarkedAsObsolete
from product_catalog_context.domain.product.events import ProductDataChanged
from product_catalog_context.infrastructure.aiosqlite_repository.product_issue_repository import ProductIssueRepository

class ProductDataChangedHandler:
  def __init__(self, unit_of_work_factory: UnitOfWorkFactory):
    self.unit_of_work_factory = unit_of_work_factory

  async def handle(self, event: ProductDataChanged):
    async with self.unit_of_work_factory() as uow:
      for field in event.fields:
        issue = await uow.product_issues.get_pending_issue(product_id=event.product_id, reported_field=field)
        if issue is not None:
          try:
            issue.mark_as_obsolete()
          except IssueCanNotBeMarkedAsObsolete:
            continue
          await uow.product_issues.save(issue)
