from product_catalog_context.domain.product.events import ProductCategoryChangedInHierarchy
from product_catalog_context.infrastructure.aiosqlite_repository.category_assignment_task_repository import CategoryAssignmentTaskRepository

class ProductCategoryChangedHandler:
  def __init__(self, category_assignment_task_repository: CategoryAssignmentTaskRepository):
    self.category_assignment_task_repository = category_assignment_task_repository

  async def handle(self, event: ProductCategoryChangedInHierarchy): #will be have own uow (i will add it soon)
    task = self.category_assignment_task_repository.get_by_product_and_hierarchy(event.product_id, event.hierarchy_id)
    if task is None:
      return
    if task.user_id == event.changed_by:
      task.complete()
    else:
      task.cancel()
    await self.category_assignment_task_repository.update(task)