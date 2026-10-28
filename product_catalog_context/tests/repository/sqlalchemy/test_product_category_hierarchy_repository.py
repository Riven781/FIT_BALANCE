import pytest
from product_catalog_context.domain.category_hierarchy.product_category_hierarchy_repository import ProductCategoryHierarchyRepository
from product_catalog_context.domain.category_hierarchy.product_category_hierarchy_status import ProductCategoryHierarchyStatus
from product_catalog_context.domain.category_hierarchy.product_category_hierarchy import ProductCategoryHierarchy
from product_catalog_context.domain.category_hierarchy.product_category import ProductCategory, ProductCategoryDraft, ProductCategoryNode


pytestmark = pytest.mark.usefixtures("insert_data")

@pytest.mark.asyncio
async def test_get_by_id(product_category_hierarchy_repository: ProductCategoryHierarchyRepository):
  hierarchy = await product_category_hierarchy_repository.get_by_id(1)
  assert hierarchy.hierarchy_id == 1
  assert hierarchy.status == ProductCategoryHierarchyStatus.ACTIVE
  assert len(hierarchy.product_categories) == 5


@pytest.mark.asyncio
async def test_get_draft(product_category_hierarchy_repository: ProductCategoryHierarchyRepository):
  hierarchy = await product_category_hierarchy_repository.get_draft()
  assert hierarchy.status == ProductCategoryHierarchyStatus.DRAFT
  assert hierarchy.hierarchy_id == 3
  assert len(hierarchy.product_categories) == 5

@pytest.mark.asyncio
async def test_get_planned_for_publication(product_category_hierarchy_repository: ProductCategoryHierarchyRepository):
  hierarchy = await product_category_hierarchy_repository.get_planned_for_publication()
  assert hierarchy.status == ProductCategoryHierarchyStatus.PLANNED_FOR_PUBLICATION
  assert hierarchy.hierarchy_id == 2
  assert len(hierarchy.product_categories) == 5

@pytest.mark.asyncio
async def test_get_active(product_category_hierarchy_repository: ProductCategoryHierarchyRepository):
  hierarchy = await product_category_hierarchy_repository.get_active()
  assert hierarchy.status == ProductCategoryHierarchyStatus.ACTIVE
  assert hierarchy.hierarchy_id == 1
  assert len(hierarchy.product_categories) == 5

@pytest.mark.asyncio
async def test_save_new_hierarchy(product_category_hierarchy_repository: ProductCategoryHierarchyRepository):
  product_categories = [
    ProductCategory(name='Wszystko', parent_id=None, category_id=100),
    ProductCategory(name='Słodycze', parent_id=100, category_id=101)
  ]
  new_hierarchy = ProductCategoryHierarchy(product_categories=product_categories, status=ProductCategoryHierarchyStatus.DRAFT)
  await product_category_hierarchy_repository.save(new_hierarchy)
  hierarchy = await product_category_hierarchy_repository.get_by_id(new_hierarchy.hierarchy_id)
  assert hierarchy.status == ProductCategoryHierarchyStatus.DRAFT
  assert hierarchy.hierarchy_id == 4
  assert len(hierarchy.product_categories) ==  2
  assert 'Wszystko' in [category.name for category in hierarchy.product_categories]

@pytest.mark.asyncio
async def test_save_existing_hierarchy(product_category_hierarchy_repository: ProductCategoryHierarchyRepository):
  hierarchy = await product_category_hierarchy_repository.get_by_id(3)
  product_categories = [
    ProductCategory(name='Wszystko', parent_id=None, category_id=100),
    ProductCategory(name='Słodycze', parent_id=100, category_id=101)
  ]
  hierarchy.update_categories(product_categories)
  hierarchy.start_planning_for_publication()
  await product_category_hierarchy_repository.save(hierarchy)
  loaded_hierarchy = await product_category_hierarchy_repository.get_by_id(3)
  assert loaded_hierarchy.status == ProductCategoryHierarchyStatus.PLANNING_FOR_PUBLICATION
  assert loaded_hierarchy.hierarchy_id == 3
  assert len(loaded_hierarchy.product_categories) ==  2
  assert 'Wszystko' in [category.name for category in loaded_hierarchy.product_categories]

@pytest.mark.asyncio
async def test_delete_hierarchy(product_category_hierarchy_repository: ProductCategoryHierarchyRepository, db_session):
  hierarchy = await product_category_hierarchy_repository.get_by_id(3)
  await product_category_hierarchy_repository.delete(hierarchy)
  await db_session.commit()
  loaded_hierarchy = await product_category_hierarchy_repository.get_by_id(3)
  assert loaded_hierarchy is None


@pytest.mark.asyncio
async def test_delete_active(product_category_hierarchy_repository: ProductCategoryHierarchyRepository):
  await product_category_hierarchy_repository.delete_active()
  hierarchy = await product_category_hierarchy_repository.get_by_id(1)
  assert hierarchy is None


@pytest.mark.asyncio
async def test_next_category_id(product_category_hierarchy_repository: ProductCategoryHierarchyRepository):
  id_1 = await product_category_hierarchy_repository.next_category_id()
  id_2 = await product_category_hierarchy_repository.next_category_id()
  id_3 = await product_category_hierarchy_repository.next_category_id()

  assert id_1 == 99
  assert id_2 == 100
  assert id_3 == 101
