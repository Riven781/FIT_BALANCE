from product_catalog_context.infrastructure.aiosqlite_queries.product import ProductQueries
from product_catalog_context.infrastructure.aiosqlite_repository.product_category import ProductCategoryRepository
from product_catalog_context.infrastructure.aiosqlite_repository.product_category_hierarchy import ProductCategoryHierarchyRepository
from product_catalog_context.infrastructure.api.rest.schemas.product_category import ProductCategory, ProductCategoryCreate, ProductCategoryHierarchy, ProductCategoryUpdate


class ProductCategoryService():

  def __init__(
      self,
      product_category_repository : ProductCategoryRepository,
      product_category_hierarchy_repository : ProductCategoryHierarchyRepository,
  ):
    self.product_category_repository = product_category_repository
    self.product_category_hierarchy_repository = product_category_hierarchy_repository

  async def get_hierarchy(self) -> list[ProductCategoryHierarchy]:
    return await self.product_category_hierarchy_repository.get()
  
  async def get_all(self) -> list[ProductCategory]:
    return await self.product_category_repository.get_all()
  
  async def update_hierarchy(self, new_product_categories: list[ProductCategory]): #todo chceck tree structure add product ctegory updatee
    old_product_categories = await self.product_category_repository.get_all()
    old_category_by_id_dict = {old_product_category.id : old_product_category for old_product_category in old_product_categories}
    new_category_by_id_dict = {new_product_category.id : new_product_category for new_product_category in new_product_categories}

    category_ids_to_delete = self._get_category_ids_to_delete(old_category_by_id_dict, new_category_by_id_dict)
    if category_ids_to_delete:
      await self.product_category_repository.delete(category_ids_to_delete)

    categories_to_create = self._get_categories_to_create(old_category_by_id_dict, new_category_by_id_dict)
    if categories_to_create:
      await self.product_category_repository.insert(categories_to_create)

    categories_by_id_to_update = self._get_categories_by_id_to_update(old_category_by_id_dict, new_category_by_id_dict)
    if categories_by_id_to_update:
      await self.product_category_repository.update(categories_by_id_to_update.keys(), categories_by_id_to_update.values())

    if self._is_hierarchy_structure_changed(old_category_by_id_dict, new_category_by_id_dict):
      self.product_category_hierarchy_repository.rebuild_hierarchy()
      



  def _get_categories_to_create(self, old_category_by_id_dict, new_category_by_id_dict):
    return [ProductCategoryCreate(**new_category_by_id_dict[new_category_id].model_dump()) for new_category_id in new_category_by_id_dict if new_category_id not in old_category_by_id_dict]
  
  def _get_category_ids_to_delete(self, old_category_by_id_dict, new_category_by_id_dict):
    return [old_category_id for old_category_id in old_category_by_id_dict if old_category_id not in new_category_by_id_dict]
  
  def _get_categories_by_id_to_update(self, old_category_by_id_dict, new_category_by_id_dict):
    return {new_category_id : ProductCategoryUpdate(**new_category_by_id_dict[new_category_id].model_dump()) for new_category_id in new_category_by_id_dict if new_category_id in old_category_by_id_dict and new_category_by_id_dict[new_category_id] != old_category_by_id_dict[new_category_id]}
  
  def _is_hierarchy_structure_changed(self, old_category_by_id_dict, new_category_by_id_dict):
    if len(old_category_by_id_dict) != len(new_category_by_id_dict):
      return True
    if self._get_category_ids_to_delete(old_category_by_id_dict, new_category_by_id_dict):
      return True
    if [new_category_id for new_category_id in new_category_by_id_dict if new_category_id in old_category_by_id_dict and new_category_by_id_dict[new_category_id].parent_id != old_category_by_id_dict[new_category_id].parent_id]:
      return True
    return False
      

