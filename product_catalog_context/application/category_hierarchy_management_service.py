from httpx import delete

from product_catalog_context.application.command.category_hierarchy import EditHierarchyCommand
from product_catalog_context.application.errors.errors import CategoryHierarchyDoesNotExist, DraftCategoryHierarchyExists, CategoryDoesNotBelongToHierarchy, AccessDenied
from product_catalog_context.application.unit_of_work import UnitOfWork
from product_catalog_context.infrastructure.adapters.event_dispatcher import EventDispatcher
from product_catalog_context.domain.category_hierarchy.product_category_hierarchy import ProductCategoryHierarchy
from product_catalog_context.infrastructure.adapters.access_adapter import AccessAdapter
from product_catalog_context.infrastructure.aiosqlite_queries.product import ProductQueries
from product_catalog_context.infrastructure.aiosqlite_repository.product import ProductRepository
from product_catalog_context.infrastructure.aiosqlite_repository.product_category_hierarchy import ProductCategoryHierarchyRepository
from product_catalog_context.infrastructure.api.rest.schemas.product_category import  ProductCategoryCreate, ProductCategoryUpdate
from product_catalog_context.domain.category_hierarchy.product_category import ProductCategory, ProductCategoryDraft, ProductCategoryItem


class CategoryHierarchyManagementService():

  def __init__(
      self,
      unit_of_work: UnitOfWork,
      access_adapter: AccessAdapter,
      event_dispatcher: EventDispatcher = None
  ):
    self.unit_of_work = unit_of_work
    self.access_adapter = access_adapter
    self.event_dispatcher = event_dispatcher

  async def get_hierarchy(self, hierarchy_id) -> ProductCategoryHierarchy:
    hierarchy = await self.unit_of_work.product_category_hierarchies.get_by_id(hierarchy_id)
    if hierarchy is None:
      raise CategoryHierarchyDoesNotExist()
    return hierarchy

  async def edit_hierarchy(self, command: EditHierarchyCommand):
    catalog_manager = await self.access_adapter.get_catalog_manager_for(command.catalog_manager_id)
    if catalog_manager is None:
      raise AccessDenied()
    
    async with self.unit_of_work as uow:
      hierarchy : ProductCategoryHierarchy = await uow.product_category_hierarchies.get_by_id(command.hierarchy_id)
      if hierarchy is None:
        raise CategoryHierarchyDoesNotExist()
      existing_categories = [ProductCategory(category_id=category.category_id, name=category.name, parent_id=category.parent_id, source_node_id=category.source_node_id) for category in command.existing_categories]
      draft_categories = [ProductCategoryDraft(temp_id=category.temp_id, name=category.name, parent_id=category.parent_id) for category in command.draft_categories]
      ids = [await uow.product_category_hierarchies.next_category_id() for _ in command.draft_categories]
      hierarchy.edit(existing_categories, draft_categories, ids)
      await uow.product_category_hierarchies.save(hierarchy)
    return hierarchy


  async def create_draft(self, hierarchy_id, catalog_manager_id): #TODO: event, event handler
    catalog_manager = await self.access_adapter.get_catalog_manager_for(catalog_manager_id)
    if catalog_manager is None:
      raise AccessDenied()
    
    async with self.unit_of_work as uow:
      draft_hierarchy = await uow.product_category_hierarchies.get_draft()
      if draft_hierarchy is not None:
        raise DraftCategoryHierarchyExists()
      hierarchy = await uow.product_category_hierarchies.get_by_id(hierarchy_id)
      hierarchy.ensure_draft_be_created()

      ids = [await uow.product_category_hierarchies.next_category_id() for _ in range(hierarchy.product_categories_len())]

      new_hierarchy = hierarchy.create_draft_based_on_hierarchy(ids, catalog_manager_id) #it should generate event: HierarchyDraftCreated
      await uow.product_category_hierarchies.save(new_hierarchy)
    
      await uow.products.copy_category_assignments(hierarchy.hierarchy_id, new_hierarchy.hierarchy_id) #it should be done in handler
    return new_hierarchy

  async def delete_draft(self, hierarchy_id, catalog_manager_id):
    catalog_manager = await self.access_adapter.get_catalog_manager_for(catalog_manager_id)
    if catalog_manager is None:
      raise AccessDenied()
    async with self.unit_of_work as uow:
      draft_hierarchy = await uow.product_category_hierarchies.get_by_id(hierarchy_id)
      if draft_hierarchy is None:
        raise CategoryHierarchyDoesNotExist()
      draft_hierarchy.ensure_draft_be_deleted()
      await uow.product_category_hierarchies.delete(draft_hierarchy)

  async def revert_to_draft(self, hierarchy_id, catalog_manager_id):
    catalog_manager = await self.access_adapter.get_catalog_manager_for(catalog_manager_id)
    if catalog_manager is None:
      raise AccessDenied()
    async with self.unit_of_work as uow:
      hierarchy = await uow.product_category_hierarchies.get_by_id(hierarchy_id)
      hierarchy.revert_to_draft()
      await uow.product_category_hierarchies.save(hierarchy)
      events = hierarchy.pull_events()
    if self.event_dispatcher:
      self.event_dispatcher.dispatch(events)
    return hierarchy


  async def publish_hierarchy(self, hierarchy_id, catalog_manager_id):
    catalog_manager = await self.access_adapter.get_catalog_manager_for(catalog_manager_id)
    if catalog_manager is None:
      raise AccessDenied()
    async with self.unit_of_work as uow:
      hierarchy = await uow.product_category_hierarchies.get_by_id(hierarchy_id)
      await uow.product_category_hierarchies.delete_active()
      hierarchy.publish(catalog_manager_id)
      await uow.product_category_hierarchies.save(hierarchy)
      events = hierarchy.pull_events()
    if self.event_dispatcher:
      self.event_dispatcher.dispatch(events)
    return hierarchy

  async def plan_for_publication(self, hierarchy_id, catalog_manager_id):#TODO: event, event handler
    catalog_manager = await self.access_adapter.get_catalog_manager_for(catalog_manager_id)
    if catalog_manager is None:
      raise AccessDenied()
    async with self.unit_of_work as uow:
      hierarchy = await  uow.product_category_hierarchies.get_by_id(hierarchy_id)
      hierarchy.plan_for_publication()  #generate event HierarchyPlannedForPublication
      await uow.product_category_hierarchies.save(hierarchy)
      category_ids = hierarchy.get_non_leaf_category_ids()  #in handler
      await uow.products.delete_category_assignments_by_category_id(category_ids)
    return hierarchy

