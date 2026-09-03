from httpx import delete

from product_catalog_context.application.errors.errors import CategoryHierarchyDoesNotExist, DraftCategoryHierarchyExists, CategoryDoesNotBelongToHierarchy, AccessDenied
from product_catalog_context.domain.event_dispatcher import EventDispatcher
from product_catalog_context.domain.category_hierarchy.product_category_hierarchy import ProductCategoryHierarchy
from product_catalog_context.infrastructure.adapters.access_adapter import AccessAdapter
from product_catalog_context.infrastructure.aiosqlite_queries.product import ProductQueries
from product_catalog_context.infrastructure.aiosqlite_repository.product import ProductRepository
from product_catalog_context.infrastructure.aiosqlite_repository.product_category import ProductCategoryRepository
from product_catalog_context.infrastructure.aiosqlite_repository.product_category_hierarchy import ProductCategoryHierarchyRepository
from product_catalog_context.infrastructure.api.rest.schemas.product_category import  ProductCategoryCreate, ProductCategoryUpdate
from product_catalog_context.domain.product_category import ProductCategory, ProductCategoryDraft, ProductCategoryItem


class CategoryHierarchyManagementService():

  def __init__(
      self,
      product_category_hierarchy_repository : ProductCategoryHierarchyRepository,
      access_adapter: AccessAdapter,
      product_repository : ProductRepository = None,
      event_dispatcher: EventDispatcher = None
  ):
    self.access_adapter = access_adapter
    self.product_category_hierarchy_repository = product_category_hierarchy_repository
    self.product_repository = product_repository
    self.event_dispatcher = event_dispatcher

  async def get_hierarchy(self, hierarchy_id) -> ProductCategoryHierarchy:
    return await self.product_category_hierarchy_repository.get_by_id(hierarchy_id)

  async def edit_hierarchy(self, hierarchy_id: int, product_categories: list[ProductCategory | ProductCategoryDraft], catalog_manager_id):
    catalog_manager = await self.access_adapter.get_catalog_manager_for(catalog_manager_id)
    if catalog_manager is None:
      raise AccessDenied()
    
    hierarchy : ProductCategoryHierarchy = await self.product_category_hierarchy_repository.get_by_id(hierarchy_id)

    existing_product_categories = [category for category in product_categories if type(category) is ProductCategory]
    
    are_in_hierarchy = hierarchy.contains_all_product_categories(existing_product_categories)
    if not are_in_hierarchy:
      raise CategoryDoesNotBelongToHierarchy()
    
    draft_product_categories = [category for category in product_categories if type(category) is ProductCategoryDraft]
    temp_to_id = {draft_category.temp_id: await self.product_category_hierarchy_repository.next_category_id() for draft_category in draft_product_categories}
    new_categories = [ProductCategory(name=item.name, category_id=temp_to_id[item.temp_id], parent_id=temp_to_id[item.parent_id] if item.parent_id in temp_to_id else item.parent_id) for item in draft_product_categories]
    categories = existing_product_categories + new_categories
   
    hierarchy.update_categories(categories)

    await self.product_category_hierarchy_repository.update(hierarchy.hierarchy_id, hierarchy)
    return hierarchy

  async def create_draft(self, hierarchy_id, catalog_manager_id):
    catalog_manager = await self.access_adapter.get_catalog_manager_for(catalog_manager_id)
    if catalog_manager is None:
      raise AccessDenied()
    
    draft_hierarchy = await self.product_category_hierarchy_repository.get_draft()
    if draft_hierarchy is not None:
      raise DraftCategoryHierarchyExists()
    hierarchy = await self.product_category_hierarchy_repository.get_by_id(hierarchy_id)
    hierarchy.ensure_draft_be_created()

    ids = [await self.product_category_hierarchy_repository.next_category_id() for _ in range(hierarchy.product_categories_len())]

    new_hierarchy = hierarchy.create_draft_based_on_hierarchy(ids, catalog_manager_id)
    
    hierarchy_id = await self.product_category_hierarchy_repository.insert(new_hierarchy)
    new_hierarchy.hierarchy_id = hierarchy_id
  
    await self.product_repository.copy_category_assignments(hierarchy.hierarchy_id, hierarchy_id)
    return new_hierarchy

  async def delete_draft(self, hierarchy_id, catalog_manager_id):
    catalog_manager = await self.access_adapter.get_catalog_manager_for(catalog_manager_id)
    if catalog_manager is None:
      raise AccessDenied()
    
    draft_hierarchy = await self.product_category_hierarchy_repository.get_by_id(hierarchy_id)
    if draft_hierarchy is None:
      raise CategoryHierarchyDoesNotExist()
    draft_hierarchy.ensure_draft_be_deleted()
    await self.product_category_hierarchy_repository.delete(draft_hierarchy.hierarchy_id)

  async def revert_to_draft(self, hierarchy_id, catalog_manager_id):
    catalog_manager = await self.access_adapter.get_catalog_manager_for(catalog_manager_id)
    if catalog_manager is None:
      raise AccessDenied()
    hierarchy = await self.product_category_hierarchy_repository.get_by_id(hierarchy_id)
    hierarchy.revert_to_draft()
    await self.product_category_hierarchy_repository.update(hierarchy.hierarchy_id,hierarchy)
    events = hierarchy.pull_events()
    #without uow:
    if self.event_dispatcher:
      self.event_dispatcher.dispatch(events)

    return hierarchy


  async def publish_hierarchy(self, hierarchy_id, catalog_manager_id):
    catalog_manager = await self.access_adapter.get_catalog_manager_for(catalog_manager_id)
    if catalog_manager is None:
      raise AccessDenied()
    hierarchy = await self.product_category_hierarchy_repository.get_by_id(hierarchy_id)
    hierarchy.publish(catalog_manager_id)
    await self.product_category_hierarchy_repository.delete_active()
    await self.product_category_hierarchy_repository.update(hierarchy.hierarchy_id,hierarchy)
    events = hierarchy.pull_events()
    #without uow:
    if self.event_dispatcher:
      self.event_dispatcher.dispatch(events)
    return hierarchy

  async def plan_for_publication(self, hierarchy_id, catalog_manager_id):
    catalog_manager = await self.access_adapter.get_catalog_manager_for(catalog_manager_id)
    if catalog_manager is None:
      raise AccessDenied()
    hierarchy = await self.product_category_hierarchy_repository.get_by_id(hierarchy_id)
    hierarchy.plan_for_publication()
    await self.product_category_hierarchy_repository.update(hierarchy_id, hierarchy)
    category_ids = hierarchy.get_non_leaf_category_ids()
    await self.product_repository.delete_category_assignments(category_ids)
    return hierarchy

