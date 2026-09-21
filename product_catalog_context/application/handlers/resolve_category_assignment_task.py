from product_catalog_context.application.unit_of_work import UnitOfWork, UnitOfWorkFactory
from product_catalog_context.domain.product.events import ProductCategoryChangedInHierarchy
from product_catalog_context.domain.repository.errors import ConcurrentModification
from product_catalog_context.infrastructure.aiosqlite_repository.category_assignment_task_repository import CategoryAssignmentTaskRepository

class ResolveCategoryAssignmentTask:
  def __init__(self, unit_of_work_factory: UnitOfWorkFactory):
    self.unit_of_work_factory = unit_of_work_factory

  async def handle(self, event: ProductCategoryChangedInHierarchy):
    try:
      async with self.unit_of_work_factory() as uow:
        task = await uow.category_assignment_tasks.get_by_product_and_hierarchy(event.product_id, event.hierarchy_id)
        if task is None:
          return
        if task.user_id == event.changed_by:
          task.complete(event.changed_by)
        else:
          task.cancel()
        
          await uow.category_assignment_tasks.save(task)
    except ConcurrentModification:
      pass