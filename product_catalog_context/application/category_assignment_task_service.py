import math

from product_catalog_context.application.errors.errors import AccessDenied, CategoryAssignmentBelongsToAnotherUser, CategoryAssignmentRequiresProductEditor, CategoryDoesNotBelongToHierarchy, CategoryHierarchyDoesNotExist, ProductNotFoundError, TaskDoesNotExist, TaskNotFoundError, TasksBelongToDifferentHierarchies, UserIdRequired
from product_catalog_context.application.unit_of_work import UnitOfWork
from product_catalog_context.domain.tasks.allocation.calculate_allocation_plan import calculate_allocation_plan
from product_catalog_context.domain.tasks.category_assignment_task import CategoryAssignmentTask
from product_catalog_context.domain.tasks.category_assignment_task_status import CategoryAssignmentTaskStatus
from product_catalog_context.domain.product.product import Product
from product_catalog_context.infrastructure.adapters.access_adapter import AccessAdapter
from product_catalog_context.infrastructure.aiosqlite_repository.category_assignment_task_repository import CategoryAssignmentTaskRepository
from product_catalog_context.infrastructure.aiosqlite_repository.product import ProductRepository
from product_catalog_context.infrastructure.aiosqlite_repository.product_category_hierarchy import ProductCategoryHierarchyRepository

class CategoryAssignmentTaskService:
  def __init__(
      self,
      unit_of_work: UnitOfWork,
      access_adapter: AccessAdapter):   #change to access port
    self.unit_of_work = unit_of_work
    self.access_adapter = access_adapter

  async def get_task(self, task_id):
    task = await self.unit_of_work.category_assignment_tasks.get_by_id(task_id)
    if task is None:
      raise TaskDoesNotExist()
    return task

  async def complete_category_assignment(self, task_id, category_id, product_editor_id): #TODO: apply events in the future
    product_editor = await self.access_adapter.get_product_editor_for(product_editor_id)
    if product_editor is None:
      raise AccessDenied()
    async with self.unit_of_work as uow:

      task = await uow.category_assignment_tasks.get_by_id(task_id)
      if task is None:
        raise TaskDoesNotExist()

      hierarchy = await uow.product_category_hierarchies.get_by_id(task.hierarchy_id)
      if hierarchy is None:
        raise CategoryHierarchyDoesNotExist()
      
      product : Product = await uow.products.get_by_id(task.product_id)  #it should be at event handler in the future
      if product is None:
        raise ProductNotFoundError()

      hierarchy.ensure_can_complete_task(category_id)
      task.complete(product_editor_id)  #it should generate event TaskAssignmentCompleted
      product.assign_to_category(hierarchy.hierarchy_id, category_id, product_editor_id)

      await uow.products.save(product)
      await uow.category_assignment_tasks.save(task)


  async def assign_tasks_for_user_by_active_category_id(self, catalog_manager_id, product_editor_id, hierarchy_id, current_category_id, limit):
    catalog_manager = await self.access_adapter.get_catalog_manager_for(catalog_manager_id)
    if catalog_manager is None:
      raise AccessDenied()

    product_editor = await self.access_adapter.get_product_editor_for(product_editor_id)
    if product_editor is None:
      raise CategoryAssignmentRequiresProductEditor()
    
    async with self.unit_of_work as uow:
      hierarchy = await uow.product_category_hierarchies.get_by_id(hierarchy_id)
      if hierarchy is None:
        raise CategoryHierarchyDoesNotExist()
      hierarchy.ensure_can_assign_tasks()

      products = await uow.products.get_without_planned_category_and_assignment_task(current_category_id, hierarchy_id, limit)
      tasks = []
      for product in products:
        tasks.append(CategoryAssignmentTask(product_id=product.product_id, hierarchy_id=hierarchy_id, user_id=product_editor_id, status=CategoryAssignmentTaskStatus.PENDING))
      await uow.category_assignment_tasks.insert_all(tasks)

  async def allocate_tasks_for_users(self, catalog_manager_id, product_editor_ids, hierarchy_id): #automaticcly
    catalog_manager = await self.access_adapter.get_catalog_manager_for(catalog_manager_id)
    if catalog_manager is None:
      raise AccessDenied()

    for user_id in product_editor_ids:
      product_editor = await self.access_adapter.get_product_editor_for(user_id)
      if product_editor is None:
        raise CategoryAssignmentRequiresProductEditor()
  
    async with self.unit_of_work as uow:
      hierarchy = await uow.product_category_hierarchies.get_by_id(hierarchy_id)
      if hierarchy is None:
        raise CategoryHierarchyDoesNotExist()
      unassigned_products_count = await uow.products.get_total_without_planned_category()
      active_tasks_count = await uow.category_assignment_tasks.get_total_in_hierarchy(hierarchy_id)

      task_allocation_plan = calculate_allocation_plan(hierarchy, unassigned_products_count, active_tasks_count, product_editor_ids)
      if task_allocation_plan.has_tasks_to_assign:
        #maybe we should have metod execute_allocation_plan in category_assignment_tasks
        for user_id in task_allocation_plan.assigned_editor_ids:
          await uow.category_assignment_tasks.insert_tasks_for_unassigned_products(user_id, hierarchy_id, task_allocation_plan.limit_per_user)

  async def delete_task(self, task_id, catalog_manager_id):
    catalog_manager = await self.access_adapter.get_catalog_manager_for(catalog_manager_id)
    if catalog_manager is None:
      raise AccessDenied()
    async with self.unit_of_work as uow:
      task = await uow.category_assignment_tasks.get_by_id(task_id)
      if task is None:
        raise TaskNotFoundError()
      await uow.category_assignment_tasks.delete(task)


  async def delete_tasks_by_user(self, catalog_manager_id, user_id):
    catalog_manager = await self.access_adapter.get_catalog_manager_for(catalog_manager_id)
    if catalog_manager is None:
      raise AccessDenied()
    async with self.unit_of_work as uow:
      count = await uow.category_assignment_tasks.delete_by_user(user_id)
    if count == 0:
      raise TaskNotFoundError()

  async def delete_task_by_user_and_product(self, user_id, product_id, catalog_manager_id):
    catalog_manager = await self.access_adapter.get_catalog_manager_for(catalog_manager_id)
    if catalog_manager is None:
      raise AccessDenied()
    async with self.unit_of_work as uow:
      count = await uow.category_assignment_tasks.delete_by_user_and_product(user_id, product_id)
      if count == 0:
        raise TaskNotFoundError()
