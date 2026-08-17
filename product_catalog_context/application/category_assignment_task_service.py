import math

from product_catalog_context.application.errors.errors import CategoryDoesNotBelongToHierarchy, CategoryHierarchyDoesNotExist, ProductNotFoundError, TaskDoesNotExist, TaskNotFoundError, TasksBelongToDifferentHierarchies, UserIdRequired
from product_catalog_context.domain.category_assignment_task import CategoryAssignmentTask
from product_catalog_context.domain.enums.category_assignment_task_status import CategoryAssignmentTaskStatus
from product_catalog_context.domain.product import Product
from product_catalog_context.infrastructure.aiosqlite_repository.category_assignment_task_repository import CategoryAssignmentTaskRepository
from product_catalog_context.infrastructure.aiosqlite_repository.product import ProductRepository
from product_catalog_context.infrastructure.aiosqlite_repository.product_category_hierarchy import ProductCategoryHierarchyRepository


class CategoryAssignmentTaskService:
  def __init__(self, category_assignment_task_repository : CategoryAssignmentTaskRepository, product_category_hierarchy_repository : ProductCategoryHierarchyRepository, product_repository : ProductRepository):
    self.category_assignment_task_repository = category_assignment_task_repository
    self.product_category_hierarchy_repository = product_category_hierarchy_repository
    self.product_repository = product_repository

  async def get_task(self, task_id):
    task = await self.category_assignment_task_repository.get_by_id(task_id)
    if task is None:
      raise TaskDoesNotExist()
    return task

  async def complete_category_assignment(self, task_id, category_id):
    task = await self.category_assignment_task_repository.get_by_id(task_id)
    if task is None:
      raise TaskDoesNotExist()
    
    hierarchy = await self.product_category_hierarchy_repository.get_by_id(task.hierarchy_id)
    if hierarchy is None:
      return CategoryHierarchyDoesNotExist()

    if not hierarchy.contains_product_category(category_id):
      return CategoryDoesNotBelongToHierarchy()

    hierarchy.ensure_category_assignment_allowed()

    product : Product = await self.product_repository.get_by_id(task.product_id)
    if product is None:
      raise ProductNotFoundError()

    product.assign_to_planned_category(category_id)
    task.complete()

    await self.product_repository.update(product.product_id, product)
    await self.category_assignment_task_repository.update(task.task_id, task)
  """
  async def assign_tasks_for_user_by_source_category(self, user_id, hierarchy_id, source_node_id, limit):
    hierarchy = await self.product_category_hierarchy_repository.get_by_id(hierarchy_id)
    if hierarchy is None:
      return CategoryHierarchyDoesNotExist()
    hierarchy.ensure_category_assignment_allowed()
    products = await self.product_repository.get_by_current_category_id(source_node_id, limit)
    tasks = []
    for product in products:
      tasks.append(CategoryAssignmentTask(product_id=product.product_id, hierarchy_id=hierarchy_id, user_id=user_id, status=CategoryAssignmentTaskStatus.PENDING))
    await self.category_assignment_task_repository.insert(tasks)
  """
  async def assign_tasks_for_user_by_active_category_id(self, user_id, hierarchy_id, current_category_id, limit):
    hierarchy = await self.product_category_hierarchy_repository.get_by_id(hierarchy_id)
    if hierarchy is None:
      return CategoryHierarchyDoesNotExist()
    hierarchy.ensure_category_assignment_allowed()
    products = await self.product_repository.get_without_planned_category_and_task(current_category_id, hierarchy_id, limit)
    tasks = []
    for product in products:
      tasks.append(CategoryAssignmentTask(product_id=product.product_id, hierarchy_id=hierarchy_id, user_id=user_id, status=CategoryAssignmentTaskStatus.PENDING))
    await self.category_assignment_task_repository.insert(tasks)

  async def assign_tasks_for_users(self, user_ids, hierarchy_id): #automaticcly
    if user_ids == []:
      raise UserIdRequired()
    hierarchy = await self.product_category_hierarchy_repository.get_by_id(hierarchy_id)
    if hierarchy is None:
      raise CategoryHierarchyDoesNotExist()
    hierarchy.ensure_category_assignment_allowed()
    products_to_assign_len = await self.product_repository.get_total_without_planned_category()
    #rest = products_to_assign_len % len(user_ids)
    limit = math.ceil(products_to_assign_len / len(user_ids))
    
    for user_id in user_ids:
      await self.category_assignment_task_repository.insert_tasks_for_unassigned_products(user_id, hierarchy_id, limit)

  async def delete_task(self, task_id):
    count = await self.category_assignment_task_repository.delete(task_id)
    if count == 0:
      raise TaskNotFoundError()

  async def delete_tasks_by_user(self, user_id): #chcec if user has role
    count = await self.category_assignment_task_repository.delete_by_user(user_id)
    if count == 0:
      raise TaskNotFoundError()

  async def delete_task_by_user_and_product(self, user_id, product_id):
    count = await self.category_assignment_task_repository.delete_by_user_and_product(user_id, product_id)
    if count == 0:
      raise TaskNotFoundError()

"""
  async def complete_categories_assignment(self, task_ids, category_id):
    tasks = self.category_assignment_task_repository.get_by_ids(task_ids)

    if tasks == []:
      return

    hierarchy = await self.product_category_hierarchy_repository.get_by_id(tasks[0].hierarchy_id)

    if hierarchy is None:
      return CategoryHierarchyDoesNotExist()

    for task in tasks:
      if task.hierarchy_id != hierarchy.hierarchy_id:
        raise TasksBelongToDifferentHierarchies()

    if not hierarchy.contains_all_product_categories(category_id):
      return CategoryDoesNotBelongToHierarchy()
    
    hierarchy.ensure_category_assignment_allowed()


    products = await self.product_repository.get_by_ids([task.product_id for task in tasks]) #to do
    for task in tasks:
      product = products[task.product_id]

      if product is None:
        raise ProductNotFoundError()

      product.assign_to_planned_category(category_id)
      task.complete()

    #to źle bo musi być grupowy
    await self.product_repository.update(product.product_id, product)
    await self.category_assignment_task_repository.update(task.task_id, task)
"""




    

    

    