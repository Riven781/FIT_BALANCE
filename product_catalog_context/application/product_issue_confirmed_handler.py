from product_catalog_context.domain.issues.product_issue_confirmed import ProductIssueConfirmed
from product_catalog_context.infrastructure.aiosqlite_repository.product import ProductRepository


class ProductIssueConfirmedHandler:
  def __init__(self, product_repository: ProductRepository):
    self.product_repository = product_repository

  async def handle(self, event: ProductIssueConfirmed):
    product = await self.product_repository.get_by_id(event.product_id)
    if product is None:
      return

    product.resolve_issue(event.reported_field, event.resolved_value)

    await self.product_repository.update(event.product_id, product)