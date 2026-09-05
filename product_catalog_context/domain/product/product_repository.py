from abc import ABC, abstractmethod

from product_catalog_context.domain.product.product import Product


class ProductRepository(ABC):
  @abstractmethod
  async def get_without_planned_category_and_assignment_task(self, category_id, hierarchy_id, limit= 20) -> Product:
    pass

  @abstractmethod
  async def get_total_without_planned_category(self):
    pass

  @abstractmethod
  async def get_by_id(self, product_id) -> Product:
    pass

  @abstractmethod
  async def save(self, product: Product):
    pass

  @abstractmethod
  async def copy_category_assignments(self, active_hierarchy_id, draft_hierarchy_id):
    pass

  @abstractmethod
  async def delete_category_assignments_by_category_id(self, category_ids):
    pass

  @abstractmethod
  async def delete(self, product: Product):
    pass