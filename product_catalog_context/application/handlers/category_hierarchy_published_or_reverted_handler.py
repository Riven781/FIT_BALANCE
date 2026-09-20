from product_catalog_context.application.unit_of_work import UnitOfWork, UnitOfWorkFactory
from product_catalog_context.domain.category_hierarchy.events import ProductCategoryHierarchyPublished, ProductCategoryHierarchyRevertedToDraft


class CategoryHierarchyPublishedOrRevertedHandler:
  def __init__(self, unit_of_work_factory: UnitOfWorkFactory):
    self.unit_of_work_factory = unit_of_work_factory

  async def handle(self, event: ProductCategoryHierarchyPublished | ProductCategoryHierarchyRevertedToDraft):
    async with self.unit_of_work_factory() as uow:
      await uow.category_assignment_tasks.delete_by_hierarchy(event.hierarchy_id) #idempotent operation
