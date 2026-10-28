from aiosqlite import cursor
import pytest
from product_catalog_context.domain.errors import CategoryHierarchyIsNotDraft, OnlyDraftHierarchyCanBeUpdated, CategoryHierarchyCannotBeEdited
from product_catalog_context.application.command.category_hierarchy import EditHierarchyCommand, ProductCategoryDraftDTO, ProductCategoryDTO

from product_catalog_context.domain.category_hierarchy.product_category_hierarchy_status import ProductCategoryHierarchyStatus
from product_catalog_context.domain.category_hierarchy.product_category_hierarchy import ProductCategoryHierarchy
from product_catalog_context.infrastructure.aiosqlite_repository.product_category_hierarchy import ProductCategoryHierarchyRepository
from product_catalog_context.application.category_hierarchy_management_service import CategoryHierarchyManagementService
from product_catalog_context.application.errors.errors import DraftCategoryHierarchyExists, CategoryHierarchyDoesNotExist
from product_catalog_context.domain.category_hierarchy.product_category import ProductCategory, ProductCategoryDraft, ProductCategoryItem
from product_catalog_context.infrastructure.aiosqlite_repository.product import ProductRepository
from product_catalog_context.infrastructure.adapters.access_adapter import AccessAdapter

pytestmark = pytest.mark.usefixtures('insert_data')



@pytest.mark.asyncio
async def test_get_hierarchy(category_hierarchy_management_service: CategoryHierarchyManagementService):
  hierarchy = await category_hierarchy_management_service.get_hierarchy(1)
  assert len(hierarchy.product_categories) == 5
  assert hierarchy.status == ProductCategoryHierarchyStatus.ACTIVE

@pytest.mark.asyncio
async def test_create_draft_when_draft_version_exists(category_hierarchy_management_service: CategoryHierarchyManagementService, insert_draft):
  with pytest.raises(DraftCategoryHierarchyExists):
    hierarchy = await category_hierarchy_management_service.create_draft(1, catalog_manager_id=1)

@pytest.mark.asyncio
async def test_create_draft(category_hierarchy_management_service: CategoryHierarchyManagementService):
  hierarchy = await category_hierarchy_management_service.create_draft(1, 1)
  assert hierarchy.hierarchy_id == 3
  assert len(hierarchy.product_categories) == 5
  assert hierarchy.status == ProductCategoryHierarchyStatus.DRAFT
  category_0 = hierarchy.product_categories[0]
  assert category_0.name == 'Produkty' and category_0.source_node_id == 1 and category_0.parent_id is None

@pytest.mark.asyncio
async def test_plan_for_publication(category_hierarchy_management_service: CategoryHierarchyManagementService):
  hierarchy = await category_hierarchy_management_service.create_draft(1, 1)
  hierarchy_draft = await category_hierarchy_management_service.plan_for_publication(hierarchy.hierarchy_id, 1)
  assert hierarchy_draft.status == ProductCategoryHierarchyStatus.PLANNING_FOR_PUBLICATION


@pytest.mark.asyncio
async def test_plan_for_publication_active_hierarchy(category_hierarchy_management_service: CategoryHierarchyManagementService):
  with pytest.raises(CategoryHierarchyIsNotDraft):
    hierarchy = await category_hierarchy_management_service.plan_for_publication(1, 1)

@pytest.mark.asyncio
async def test_edit_hierarchy(category_hierarchy_management_service: CategoryHierarchyManagementService, insert_draft):
  existing_categories = [
    ProductCategoryDTO(name='Produkty', parent_id=None, category_id=11, source_node_id=1),
    ProductCategoryDTO(name='Roślinne', parent_id=11, category_id=12, source_node_id=2),
    ProductCategoryDTO(name='Zwierzęce', parent_id=11, category_id=13, source_node_id = 3),
  ]
  draft_categories = [
    ProductCategoryDraftDTO(name='Kurczak', parent_id=13, temp_id="temp-1")
  ]
  hierarchy = await category_hierarchy_management_service.edit_hierarchy(EditHierarchyCommand(3, existing_categories, draft_categories, 1))
  assert len(hierarchy.product_categories) == 4
  assert hierarchy.status == ProductCategoryHierarchyStatus.DRAFT
  assert hierarchy.product_categories[0].category_id == 11 and hierarchy.product_categories[0].name == 'Produkty' and hierarchy.product_categories[0].parent_id == None and hierarchy.product_categories[0].source_node_id == 1
  assert hierarchy.product_categories[1].category_id == 12 and hierarchy.product_categories[1].name == 'Roślinne' and hierarchy.product_categories[1].parent_id == 11 and hierarchy.product_categories[1].source_node_id == 2
  assert hierarchy.product_categories[2].category_id == 13 and hierarchy.product_categories[2].name == 'Zwierzęce' and hierarchy.product_categories[2].parent_id == 11 and hierarchy.product_categories[2].source_node_id == 3
  assert hierarchy.product_categories[3].category_id == 99 and hierarchy.product_categories[3].name == 'Kurczak' and hierarchy.product_categories[3].parent_id == 13 and hierarchy.product_categories[3].source_node_id == None 

@pytest.mark.asyncio
async def test_edit_active_hierarchy(category_hierarchy_management_service: CategoryHierarchyManagementService):
  with pytest.raises(CategoryHierarchyCannotBeEdited):
    hierarchy = await category_hierarchy_management_service.edit_hierarchy(EditHierarchyCommand(1, [], [], 1))


@pytest.mark.asyncio
async def test_publish(category_hierarchy_management_service: CategoryHierarchyManagementService):
  hierarchy = await category_hierarchy_management_service.publish_hierarchy(2, 1)
  assert hierarchy.status == ProductCategoryHierarchyStatus.ACTIVE
  assert hierarchy.published_by == 1
  with pytest.raises(CategoryHierarchyDoesNotExist):
    hierarchy = await category_hierarchy_management_service.get_hierarchy(1)


@pytest.mark.asyncio
async def test_revert_to_draft(category_hierarchy_management_service: CategoryHierarchyManagementService):
  hierarchy = await category_hierarchy_management_service.revert_to_draft(2, 1)
  assert hierarchy.status == ProductCategoryHierarchyStatus.DRAFT

@pytest.mark.asyncio
async def test_delete_draft(category_hierarchy_management_service: CategoryHierarchyManagementService, insert_draft):
  await category_hierarchy_management_service.delete_draft(3, 1)
  with pytest.raises(CategoryHierarchyDoesNotExist):
    hierarchy = await category_hierarchy_management_service.get_hierarchy(3)

