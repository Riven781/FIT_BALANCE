from product_catalog_context.application.unit_of_work import UnitOfWork
from product_catalog_context.domain.product.events import ProductCategoryChangedInHierarchy
from product_catalog_context.infrastructure.aiosqlite_repository.category_assignment_task_repository import CategoryAssignmentTaskRepository

class ProductCategoryChangedHandler:
  def __init__(self, unit_of_work: UnitOfWork):
    self.unit_of_work = unit_of_work

  async def handle(self, event: ProductCategoryChangedInHierarchy):
    async with self.unit_of_work as uow:
      task = await uow.category_assignment_tasks.get_by_product_and_hierarchy(event.product_id, event.hierarchy_id)
      if task is None:
        return
      if task.user_id == event.changed_by:
        task.complete()
      else:
        task.cancel()
      await uow.category_assignment_tasks.save(task)