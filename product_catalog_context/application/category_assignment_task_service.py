import math

from product_catalog_context.application.errors.errors import AccessDenied, CategoryAssignmentBelongsToAnotherUser, CategoryAssignmentRequiresProductEditor, CategoryDoesNotBelongToHierarchy, CategoryHierarchyDoesNotExist, ProductNotFoundError, TaskDoesNotExist, TaskNotFoundError, TasksBelongToDifferentHierarchies, UserIdRequired
from product_catalog_context.domain.category_assignment_task import CategoryAssignmentTask
from product_catalog_context.domain.enums.category_assignment_task_status import CategoryAssignmentTaskStatus
from product_catalog_context.domain.product import Product
from product_catalog_context.infrastructure.adapters.access_adapter import AccessAdapter
from product_catalog_context.infrastructure.aiosqlite_repository.category_assignment_task_repository import CategoryAssignmentTaskRepository
from product_catalog_context.infrastructure.aiosqlite_repository.product import ProductRepository
from product_catalog_context.infrastructure.aiosqlite_repository.product_category_hierarchy import ProductCategoryHierarchyRepository

class CategoryAssignmentTaskService:
  def __init__(
      self,
      category_assignment_task_repository : CategoryAssignmentTaskRepository, 
      product_category_hierarchy_repository : ProductCategoryHierarchyRepository, 
      product_repository : ProductRepository,
      access_adapter: AccessAdapter):   #change to access port
    self.category_assignment_task_repository = category_assignment_task_repository
    self.product_category_hierarchy_repository = product_category_hierarchy_repository
    self.product_repository = product_repository
    self.access_adapter = access_adapter

  async def get_task(self, task_id):
    task = await self.category_assignment_task_repository.get_by_id(task_id)
    if task is None:
      raise TaskDoesNotExist()
    return task

  async def complete_category_assignment(self, task_id, category_id, product_editor_id):
    product_editor = await self.access_adapter.get_product_editor_for(product_editor_id)
    if product_editor is None:
      raise AccessDenied()
    
    task = await self.category_assignment_task_repository.get_by_id(task_id)
    if task is None:
      raise TaskDoesNotExist()

    if product_editor_id != task.user_id:
      raise CategoryAssignmentBelongsToAnotherUser()
    
    hierarchy = await self.product_category_hierarchy_repository.get_by_id(task.hierarchy_id)
    if hierarchy is None:
      return CategoryHierarchyDoesNotExist()

    if not hierarchy.contains_product_category(category_id):
      return CategoryDoesNotBelongToHierarchy()

    hierarchy.ensure_category_assignment_allowed()

    product : Product = await self.product_repository.get_by_id(task.product_id)
    if product is None:
      raise ProductNotFoundError()

    product.assign_to_category(hierarchy.hierarchy_id, category_id, product_editor_id)
    task.complete()

    await self.product_repository.update(product.product_id, product)
    await self.category_assignment_task_repository.update(task.task_id, task)

  async def assign_tasks_for_user_by_active_category_id(self, catalog_manager_id, product_editor_id, hierarchy_id, current_category_id, limit):
    catalog_manager = await self.access_adapter.get_catalog_manager_for(catalog_manager_id)
    if catalog_manager is None:
      raise AccessDenied()

    product_editor = await self.access_adapter.get_product_editor_for(product_editor_id)
    if product_editor is None:
      raise CategoryAssignmentRequiresProductEditor()

    hierarchy = await self.product_category_hierarchy_repository.get_by_id(hierarchy_id)
    if hierarchy is None:
      return CategoryHierarchyDoesNotExist()
    hierarchy.ensure_category_assignment_allowed()
    products = await self.product_repository.get_without_planned_category_and_assignment_task(current_category_id, hierarchy_id, limit)
    tasks = []
    for product in products:
      tasks.append(CategoryAssignmentTask(product_id=product.product_id, hierarchy_id=hierarchy_id, user_id=product_editor_id, status=CategoryAssignmentTaskStatus.PENDING))
    await self.category_assignment_task_repository.insert(tasks)

  async def assign_tasks_for_users(self, catalog_manager_id, product_editor_ids, hierarchy_id): #automaticcly
    catalog_manager = await self.access_adapter.get_catalog_manager_for(catalog_manager_id)
    if catalog_manager is None:
      raise AccessDenied()
    
    if product_editor_ids == []:
      raise UserIdRequired()
    for user_id in product_editor_ids:
      product_editor = await self.access_adapter.get_product_editor_for(user_id)
      if product_editor is None:
        raise CategoryAssignmentRequiresProductEditor()

    hierarchy = await self.product_category_hierarchy_repository.get_by_id(hierarchy_id)
    if hierarchy is None:
      raise CategoryHierarchyDoesNotExist()
    hierarchy.ensure_category_assignment_allowed()
    products_to_assign_len = await self.product_repository.get_total_without_planned_category()
    #rest = products_to_assign_len % len(user_ids)
    limit = math.ceil(products_to_assign_len / len(product_editor_ids))
    
    for user_id in product_editor_ids:
      await self.category_assignment_task_repository.insert_tasks_for_unassigned_products(user_id, hierarchy_id, limit)

  async def delete_task(self, task_id, catalog_manager_id):
    catalog_manager = await self.access_adapter.get_catalog_manager_for(catalog_manager_id)
    if catalog_manager is None:
      raise AccessDenied()
    
    count = await self.category_assignment_task_repository.delete(task_id)
    if count == 0:
      raise TaskNotFoundError()

  async def delete_tasks_by_user(self, catalog_manager_id, user_id):
    catalog_manager = await self.access_adapter.get_catalog_manager_for(catalog_manager_id)
    if catalog_manager is None:
      raise AccessDenied()
    
    count = await self.category_assignment_task_repository.delete_by_user(user_id)
    if count == 0:
      raise TaskNotFoundError()

  async def delete_task_by_user_and_product(self, user_id, product_id, catalog_manager_id):
    catalog_manager = await self.access_adapter.get_catalog_manager_for(catalog_manager_id)
    if catalog_manager is None:
      raise AccessDenied()
    
    count = await self.category_assignment_task_repository.delete_by_user_and_product(user_id, product_id)
    if count == 0:
      raise TaskNotFoundError()
