
from aiosqlite import cursor
import pytest

from product_catalog_context.domain.category_hierarchy.product_category_hierarchy_status import ProductCategoryHierarchyStatus
from product_catalog_context.domain.category_hierarchy.product_category_hierarchy import ProductCategoryHierarchy
from product_catalog_context.infrastructure.aiosqlite_repository.product_category_hierarchy import ProductCategoryHierarchyRepository
from product_catalog_context.domain.category_hierarchy.product_category import ProductCategory

async def insert_hierarchies(db):
  cursor = await db.executescript("""
    INSERT INTO ProductCategoryHierarchy (id, status) VALUES
      (1, "ACTIVE");

    INSERT INTO ProductCategoryNode (id, name, parent_id, hierarchy_id) VALUES
      (1, "Produkty", NULL, 1),
      (2, "Roślinne", 1, 1),
      (3, "Zwierzęce", 1, 1),
      (4, "Schab", 3, 1),
      (5, "Boczek", 3, 1),
      (6, "Tofu", 2, 1),
      (7, "Groszek", 2, 1),
      (8, "Groszek Zielony", 7, 1),
      (9, "Boczek Pikantny", 5, 1);

      INSERT INTO ProductCategoryHierarchy (id, status) VALUES
        (2, "DRAFT");
    
      INSERT INTO ProductCategoryNode (id, name, parent_id, hierarchy_id) VALUES
        (10, "Produkty", NULL, 2),
        (11, "Roślinnopodobne", 10, 2),
        (12, "Zwierzęce", 10, 2),
        (13, "Schabik", 12, 2),
        (14, "Boczek", 12, 2),
        (15, "Tofu", 11, 2),
        (16, "Groszek", 11, 2),
        (17, "Groszek Zielony", 16, 2),
        (18, "Boczek Pikantny", 14, 2);

                     
  """)
  await db.commit()
  await cursor.close()

@pytest.mark.asyncio
async def test_next_category_id(db):
  repo = ProductCategoryHierarchyRepository(db)
  category_id = await repo.next_category_id()
  assert category_id == 1
  category_id = await repo.next_category_id()
  assert category_id == 2

@pytest.mark.asyncio
async def test_get_hierarchy(db):
  await insert_hierarchies(db)
  repo = ProductCategoryHierarchyRepository(db)
  hierarchy = await repo.get_by_id(1)
  assert hierarchy.hierarchy_id == 1
  assert hierarchy.status == 'ACTIVE'
  assert len(hierarchy.product_categories) == 9
  assert hierarchy.product_categories[0].name == 'Produkty'


@pytest.mark.asyncio
async def test_get_not_existing_hierarchy(db):
  await insert_hierarchies(db)
  repo = ProductCategoryHierarchyRepository(db)
  hierarchy = await repo.get_by_id(100)
  assert hierarchy is None


@pytest.mark.asyncio
async def test_insert_hierarchy_without_categories(db):
  await insert_hierarchies(db)
  repo = ProductCategoryHierarchyRepository(db)
  hierarchy = ProductCategoryHierarchy(product_categories=[], status=ProductCategoryHierarchyStatus.DRAFT)
  hierarchy_id = await repo.insert(hierarchy)
  hierarchy = await repo.get_by_id(hierarchy_id)
  assert hierarchy.status == 'DRAFT'
  assert hierarchy.product_categories == []

@pytest.mark.asyncio
async def test_insert_hierarchy_with_category(db):
  await insert_hierarchies(db)
  repo = ProductCategoryHierarchyRepository(db)
  hierarchy = ProductCategoryHierarchy(product_categories=[ProductCategory(name='Czekolada', parent_id=None, category_id=100)], status=ProductCategoryHierarchyStatus.DRAFT)
  hierarchy_id = await repo.insert(hierarchy)
  hierarchy = await repo.get_by_id(hierarchy_id)
  assert hierarchy.status == 'DRAFT'
  assert len(hierarchy.product_categories) == 1
  category = hierarchy.product_categories[0]
  assert category.name == 'Czekolada' and category.parent_id is None and category.category_id == 100

@pytest.mark.asyncio
async def test_insert_hierarchy_with_categories(db):
  repo = ProductCategoryHierarchyRepository(db)
  hierarchy = ProductCategoryHierarchy(
    product_categories=[ProductCategory(name='Słodkości', parent_id=None, category_id=100), ProductCategory(name='Czekolada', parent_id=100, category_id=101)], 
    status=ProductCategoryHierarchyStatus.DRAFT)
  hierarchy_id = await repo.insert(hierarchy)
  hierarchy = await repo.get_by_id(hierarchy_id)
  assert hierarchy.status == 'DRAFT'
  assert len(hierarchy.product_categories) == 2
  category_1 = hierarchy.product_categories[0]
  assert category_1.name == 'Słodkości' and category_1.parent_id is None and category_1.category_id == 100
  category_2 = hierarchy.product_categories[1]
  assert category_2.name == 'Czekolada' and category_2.parent_id == 100 and category_2.category_id == 101

@pytest.mark.asyncio
async def test_update_not_existing_hierarchy(db): #in the future update will not need hierarchy_id
  await insert_hierarchies(db)
  repo = ProductCategoryHierarchyRepository(db)
  hierarchy = await repo.get_by_id(2)
  categories = hierarchy.product_categories + [ProductCategory(name='Mieszane', parent_id=10, category_id=100)]
  hierarchy.update_categories(categories)
  count = await repo.update(1000, hierarchy)
  assert count == 0

@pytest.mark.asyncio
async def test_update_hierarchy_adding_new_category(db):
  await insert_hierarchies(db)
  repo = ProductCategoryHierarchyRepository(db)
  hierarchy = await repo.get_by_id(2)
  categories = hierarchy.product_categories + [ProductCategory(name='Mieszane', parent_id=10, category_id=100)]
  hierarchy.update_categories(categories)
  await repo.update(hierarchy.hierarchy_id, hierarchy)
  hierarchy = await repo.get_by_id(2)
  assert len(hierarchy.product_categories) == 10

@pytest.mark.asyncio
async def test_update_hierarchy_deleting_category(db):
  await insert_hierarchies(db)
  repo = ProductCategoryHierarchyRepository(db)
  hierarchy = await repo.get_by_id(2)
  categories = [category for category in hierarchy.product_categories if category.category_id !=11]
  categories[4].parent_id = None
  categories[5].parent_id = None
  hierarchy.update_categories(categories)
  await repo.update(hierarchy.hierarchy_id, hierarchy)
  hierarchy = await repo.get_by_id(2)
  assert len(hierarchy.product_categories) == 8
  assert hierarchy.product_categories[4].name == 'Tofu' and hierarchy.product_categories[4].parent_id == None


@pytest.mark.asyncio
async def test_update_hierarchy_renaming(db):
  await insert_hierarchies(db)
  repo = ProductCategoryHierarchyRepository(db)
  hierarchy = await repo.get_by_id(2)
  categories = hierarchy.product_categories
  categories[0].rename('Wszystko')
  hierarchy.update_categories(categories)
  await repo.update(hierarchy.hierarchy_id, hierarchy)
  hierarchy = await repo.get_by_id(2)
  assert len(hierarchy.product_categories) == 9
  assert hierarchy.product_categories[0].name == 'Wszystko'

@pytest.mark.asyncio
async def test_update_hierarchy_adding_deleting_renaming(db):
  await insert_hierarchies(db)
  repo = ProductCategoryHierarchyRepository(db)
  hierarchy = await repo.get_by_id(2)
  categories = [category for category in hierarchy.product_categories if category.category_id !=17 and category.category_id != 18]
  categories = categories + [ProductCategory(name='Przekąski', parent_id=11, category_id=100), ProductCategory(name='Chipsy', parent_id=100, category_id=101)]
  categories[0].rename('Wszystko')

  hierarchy.update_categories(categories)
  await repo.update(hierarchy.hierarchy_id, hierarchy)
  hierarchy = await repo.get_by_id(2)
  assert len(hierarchy.product_categories) == 9
  assert hierarchy.product_categories[0].name == 'Wszystko'
  
  async with db.execute("SELECT * FROM  ProductCategoryNode WHERE id IN (17, 18)") as cursor:
    result = await cursor.fetchall()
  assert result == []

  async with db.execute("SELECT * FROM  ProductCategoryNode WHERE id IN (100, 101)") as cursor:
    result = await cursor.fetchall()
  assert len(result) == 2
  category_100 = [category for category in hierarchy.product_categories if category.category_id == 100][0]
  assert category_100.name == 'Przekąski' and category_100.parent_id == 11
  category_100 = [category for category in hierarchy.product_categories if category.category_id == 101][0]
  assert category_100.name == 'Chipsy' and category_100.parent_id == 100



@pytest.mark.asyncio
async def test_delete_hierarchy(db):
  await insert_hierarchies(db)
  repo = ProductCategoryHierarchyRepository(db)
  count = await repo.delete(1)
  assert count == 1

  async with db.execute("SELECT * FROM  ProductCategoryNode WHERE id IN (1, 2, 3, 4, 5, 6, 7, 8, 9)") as cursor:
    result = await cursor.fetchall()
  assert result == []


@pytest.mark.asyncio
async def test_delete_not_existing_hierarchy(db):
  await insert_hierarchies(db)
  repo = ProductCategoryHierarchyRepository(db)
  count = await repo.delete(100)
  assert count == 0


@pytest.mark.asyncio
async def test_get_draft(db):
  await insert_hierarchies(db)
  repo = ProductCategoryHierarchyRepository(db)
  hierarchy = await repo.get_draft()
  assert hierarchy.hierarchy_id == 2
  assert hierarchy.status == 'DRAFT'
  assert len(hierarchy.product_categories) == 9

@pytest.mark.asyncio
async def test_get__not_existing_draft(db):
  repo = ProductCategoryHierarchyRepository(db)
  hierarchy = await repo.get_draft()
  assert hierarchy == None

@pytest.mark.asyncio
async def test_delete_active(db):
  await insert_hierarchies(db)
  repo = ProductCategoryHierarchyRepository(db)
  count = await repo.delete_active()
  assert count == 1
  hierarchy = await repo.get_by_id(1)
  assert hierarchy is None


