from abc import ABC, abstractmethod

from product_catalog_context.domain.tasks.category_assignment_task import CategoryAssignmentTask


class CategoryAssignmentTaskRepository(ABC):

  @abstractmethod
  async def get_by_id(self, task_id) -> CategoryAssignmentTask:
    pass

  @abstractmethod
  async def get_by_product_and_hierarchy(self, product_id, hierarchy_id) -> CategoryAssignmentTask:
    pass

  @abstractmethod
  async def insert_tasks_for_unassigned_products(self, user_id, hierarchy_id, limit):
    pass

  @abstractmethod
  async def delete_by_user(self, user_id):
    pass

  @abstractmethod
  async def delete_by_hierarchy(self, hierarchy_id):
    pass
  
  @abstractmethod
  async def save(self, task: CategoryAssignmentTask):
    pass
  