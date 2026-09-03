from aiosqlite import cursor
import pytest
from product_catalog_context.domain.errors import CategoryHierarchyIsNotDraft, OnlyDraftHierarchyCanBeUpdated

from product_catalog_context.domain.enums.product_category_hierarchy_status import ProductCategoryHierarchyStatus
from product_catalog_context.domain.category_hierarchy.product_category_hierarchy import ProductCategoryHierarchy
from product_catalog_context.infrastructure.aiosqlite_repository.product_category_hierarchy import ProductCategoryHierarchyRepository
from product_catalog_context.application.category_hierarchy_management_service import CategoryHierarchyManagementService
from product_catalog_context.application.errors.errors import DraftCategoryHierarchyExists
from product_catalog_context.domain.product_category import ProductCategory, ProductCategoryDraft, ProductCategoryItem
from product_catalog_context.infrastructure.aiosqlite_repository.product import ProductRepository
from product_catalog_context.infrastructure.adapters.access_adapter import AccessAdapter

async def insert_users(db):
  cursor = await db.executescript(
    """
    INSERT INTO User(id, username, email, hashed_password) VALUES 
      (1, 'ZYZ','xyz@gm.c','xyz'), 
      (2, 'ABC','abc@gm.c','abc'),
      (3, 'OKO','oko@gm.c','oko');

    INSERT INTO UserRoles(user_id, version) VALUES 
      (1, 1), 
      (2, 1),
      (3, 1);

    INSERT INTO UserRole(user_id, role) VALUES 
      (1, 'product_editor'),
      (1, 'catalog_manager'),
      (2, 'product_editor'),
      (3, 'product_editor');
    """
  )
  await db.commit()
  await cursor.close()

async def insert_2_hierarchies(db):
  await insert_users(db)
  repo = ProductCategoryHierarchyRepository(db)
  ids = [await repo.next_category_id() for _ in range(18)]
  cursor = await db.executescript(f"""
    INSERT INTO ProductCategoryHierarchy (id, status) VALUES
      (1, "ACTIVE");

    INSERT INTO ProductCategoryNode (id, name, parent_id, hierarchy_id) VALUES
      ({ids[0]}, "Produkty", NULL, 1),
      ({ids[1]}, "Roślinne", 1, 1),
      ({ids[2]}, "Zwierzęce", 1, 1),
      ({ids[3]}, "Schab", 3, 1),
      ({ids[4]}, "Boczek", 3, 1),
      ({ids[5]}, "Tofu", 2, 1),
      ({ids[6]}, "Groszek", 2, 1),
      ({ids[7]}, "Groszek Zielony", 7, 1),
      ({ids[8]}, "Boczek Pikantny", 5, 1);

      INSERT INTO ProductCategoryHierarchy (id, status) VALUES
        (2, "DRAFT");
    
      INSERT INTO ProductCategoryNode (id, name, parent_id, hierarchy_id, source_node_id) VALUES
        ({ids[9]}, "Produkty", NULL, 2, 1),
        ({ids[10]}, "Roślinnopodobne", 10, 2, 2),
        ({ids[11]}, "Zwierzęce", 10, 2, 3),
        ({ids[12]}, "Schabik", 12, 2, 4),
        ({ids[13]}, "Boczek", 12, 2, 5),
        ({ids[14]}, "Tofu", 11, 2, 6),
        ({ids[15]}, "Groszek", 11, 2, 7),
        ({ids[16]}, "Groszek Zielony", 16, 2, 8),
        ({ids[17]}, "Boczek Pikantny", 14, 2, 9);
                            
  """)
  await db.commit()
  await cursor.close()

async def insert_1_hierarchy(db):
  await insert_users(db)
  repo = ProductCategoryHierarchyRepository(db)
  ids = [await repo.next_category_id() for _ in range(9)]
  cursor = await db.executescript(f"""
    INSERT INTO ProductCategoryHierarchy (id, status) VALUES
      (1, "ACTIVE");

    INSERT INTO ProductCategoryNode (id, name, parent_id, hierarchy_id) VALUES
      ({ids[0]}, "Produkty", NULL, 1),
      ({ids[1]}, "Roślinne", 1, 1),
      ({ids[2]}, "Zwierzęce", 1, 1),
      ({ids[3]}, "Schab", 3, 1),
      ({ids[4]}, "Boczek", 3, 1),
      ({ids[5]}, "Tofu", 2, 1),
      ({ids[6]}, "Groszek", 2, 1),
      ({ids[7]}, "Groszek Zielony", 7, 1),
      ({ids[8]}, "Boczek Pikantny", 5, 1);
  """)
  await db.commit()
  await cursor.close()


@pytest.mark.asyncio
async def test_get_hierarchy(db, access_adapter):
  await insert_2_hierarchies(db)
  repo = ProductCategoryHierarchyRepository(db)
  service = CategoryHierarchyManagementService(repo, access_adapter=access_adapter)
  hierarchy = await service.get_hierarchy(1)
  assert len(hierarchy.product_categories) == 9
  assert hierarchy.status == ProductCategoryHierarchyStatus.ACTIVE

@pytest.mark.asyncio
async def test_create_draft_when_draft_version_exists(db, access_adapter):
  await insert_2_hierarchies(db)
  repo = ProductCategoryHierarchyRepository(db)
  service = CategoryHierarchyManagementService(repo, access_adapter=access_adapter)
  with pytest.raises(DraftCategoryHierarchyExists):
    hierarchy = await service.create_draft(1, 1)


@pytest.mark.asyncio
async def test_create_draft(db, access_adapter):
  await insert_1_hierarchy(db)
  repo = ProductCategoryHierarchyRepository(db)
  service = CategoryHierarchyManagementService(repo, access_adapter, ProductRepository(db))
  hierarchy = await service.create_draft(1, 1)
  assert hierarchy.hierarchy_id == 2
  assert len(hierarchy.product_categories) == 9
  assert hierarchy.status == ProductCategoryHierarchyStatus.DRAFT
  category_0 = hierarchy.product_categories[0]
  assert category_0.category_id == 10 and category_0.name == 'Produkty' and category_0.source_node_id == 1 and category_0.parent_id is None


@pytest.mark.asyncio
async def test_plan_for_publication(db, access_adapter):
  await insert_2_hierarchies(db)
  repo = ProductCategoryHierarchyRepository(db)
  service = CategoryHierarchyManagementService(repo, access_adapter, ProductRepository(db))
  hierarchy = await service.plan_for_publication(2, 1)
  assert hierarchy.status == ProductCategoryHierarchyStatus.PLANNED_FOR_PUBLICATION

@pytest.mark.asyncio
async def test_plan_for_publication_active_hierarchy(db, access_adapter):
  await insert_2_hierarchies(db)
  repo = ProductCategoryHierarchyRepository(db)
  service = CategoryHierarchyManagementService(repo, access_adapter)
  with pytest.raises(CategoryHierarchyIsNotDraft):
    hierarchy = await service.plan_for_publication(1, 1)

@pytest.mark.asyncio
async def test_edit_hierarchy(db, access_adapter):
  await insert_2_hierarchies(db)
  repo = ProductCategoryHierarchyRepository(db)
  service = CategoryHierarchyManagementService(repo, access_adapter)
  categories = [
    ProductCategory(name='Produkty', parent_id=None, category_id=10, source_node_id=1),
    ProductCategory(name='Roślinne', parent_id=10, category_id=11, source_node_id=2),
    ProductCategory(name='Zwierzęce', parent_id=10, category_id=12, source_node_id = 3),
    ProductCategoryDraft(name='Kurczak', parent_id=12, temp_id="temp-1")
  ]
  hierarchy = await service.edit_hierarchy(2, categories, 1)
  assert len(hierarchy.product_categories) == 4
  assert hierarchy.status == ProductCategoryHierarchyStatus.DRAFT
  assert hierarchy.product_categories[0].category_id == 10 and hierarchy.product_categories[0].name == 'Produkty' and hierarchy.product_categories[0].parent_id == None and hierarchy.product_categories[0].source_node_id == 1
  assert hierarchy.product_categories[1].category_id == 11 and hierarchy.product_categories[1].name == 'Roślinne' and hierarchy.product_categories[1].parent_id == 10 and hierarchy.product_categories[1].source_node_id == 2
  assert hierarchy.product_categories[2].category_id == 12 and hierarchy.product_categories[2].name == 'Zwierzęce' and hierarchy.product_categories[2].parent_id == 10 and hierarchy.product_categories[2].source_node_id == 3
  assert hierarchy.product_categories[3].category_id == 19 and hierarchy.product_categories[3].name == 'Kurczak' and hierarchy.product_categories[3].parent_id == 12 and hierarchy.product_categories[3].source_node_id == None 

@pytest.mark.asyncio
async def test_edit_active_hierarchy(db, access_adapter):
  await insert_2_hierarchies(db)
  repo = ProductCategoryHierarchyRepository(db)
  service = CategoryHierarchyManagementService(repo, access_adapter)
  categories = []
  with pytest.raises(OnlyDraftHierarchyCanBeUpdated):
    hierarchy = await service.edit_hierarchy(1, categories, 1)


@pytest.mark.asyncio
async def test_publish(db, access_adapter):
  await insert_2_hierarchies(db)
  repo = ProductCategoryHierarchyRepository(db)
  service = CategoryHierarchyManagementService(repo, access_adapter, ProductRepository(db))
  hierarchy = await service.plan_for_publication(2, 1)
  hierarchy = await service.publish_hierarchy(2, 1)
  assert hierarchy.status == ProductCategoryHierarchyStatus.ACTIVE
  assert hierarchy.published_by == 1
  hierarchy = await service.get_hierarchy(1)
  assert hierarchy is None

@pytest.mark.asyncio
async def test_revert_to_draft(db, access_adapter):
  await insert_2_hierarchies(db)
  repo = ProductCategoryHierarchyRepository(db)
  service = CategoryHierarchyManagementService(repo, access_adapter, ProductRepository(db))
  hierarchy = await service.plan_for_publication(2, 1)
  hierarchy = await service.revert_to_draft(2, 1)
  assert hierarchy.status == ProductCategoryHierarchyStatus.DRAFT

@pytest.mark.asyncio
async def test_delete_draft(db, access_adapter):
  await insert_2_hierarchies(db)
  repo = ProductCategoryHierarchyRepository(db)
  service = CategoryHierarchyManagementService(repo, access_adapter, ProductRepository(db))
  await service.delete_draft(2, 1)
  hierarchy = await service.get_hierarchy(2)
  assert hierarchy is None

