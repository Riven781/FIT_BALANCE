from product_catalog_context.application.unit_of_work import UnitOfWork
from product_catalog_context.domain.issues.product_issue_confirmed import ProductIssueConfirmed
from product_catalog_context.infrastructure.aiosqlite_repository.product import ProductRepository


class ProductIssueConfirmedHandler:
  def __init__(self, unit_of_work: UnitOfWork):
    self.unit_of_work = unit_of_work

  async def handle(self, event: ProductIssueConfirmed):
    async with self.unit_of_work as uow:
      product = await uow.products.get_by_id(event.product_id)
      if product is None:
        return
      product.resolve_issue(event.reported_field, event.resolved_value)
      await uow.products.save(product)