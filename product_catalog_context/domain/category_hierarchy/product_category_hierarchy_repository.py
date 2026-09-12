from abc import ABC, abstractmethod

from product_catalog_context.domain.category_hierarchy.product_category_hierarchy import ProductCategoryHierarchy


class ProductCategoryHierarchyRepository(ABC):
  @abstractmethod
  async def get_by_id(self, hierarchy_id) -> ProductCategoryHierarchy | None:
    pass

  @abstractmethod
  async def get_draft(self) -> ProductCategoryHierarchy | None:
    pass

  @abstractmethod
  async def get_planned_for_publication(self) -> ProductCategoryHierarchy | None:
    pass

  @abstractmethod
  async def get_active(self) -> ProductCategoryHierarchy | None:
    pass

  @abstractmethod
  async def save(self, hierarchy: ProductCategoryHierarchy):
    pass

  @abstractmethod
  async def delete(self, hierarchy: ProductCategoryHierarchy):
    pass

  @abstractmethod
  async def delete_active(self):
    pass

  @abstractmethod
  async def next_category_id(self):
    pass