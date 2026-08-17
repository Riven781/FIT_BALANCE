import pytest
from product_catalog_context.infrastructure.aiosqlite_repository.category_assignment_task_repository import CategoryAssignmentTaskRepository
from product_catalog_context.domain.category_assignment_task import CategoryAssignmentTask
from product_catalog_context.domain.enums.category_assignment_task_status import CategoryAssignmentTaskStatus


async def insert_data(db):
  cursor = await db.executescript("""
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

      INSERT INTO Product (id, name, brand_name, kcal, reference_amount, reference_unit, name_search_standard)
        VALUES 
        (1, "Schab Drogi", "Auchan", 300, 100, "g","schab drogi"),
        (2, "Schab Tani", "Rambert", 250, 100, "g", "schab tani"),
        (3, "Schab Średni", "XYZ", 400, 100, "g", "schab sredni"),
        (4, "Tofu", "XYZ", 300, 100, "g", "tofu"),
        (5, "Groszek", "ABC", 100, 100, "g", "groszek"),                                                         
        (6, "Boczek Kaszubski", "WWW", 500, 100, "g", "boczek kaszubski"),
        (7, "Boczek Cielęcy", "YYY", 400, 100, "g", "boczek cielecy"),
        (8, "Raw Energy Baton kakaowy Bombus", "BB", 300, 100, "g", "raw energy baton kakaowy bombus");

        INSERT INTO User(id, username, email, hashed_password) VALUES 
        (1, 'ZYZ','xyz@gm.c','xyz'), (2, 'ABC','abc@gm.c','abc');

        INSERT INTO ProductCategoryAssignmentTask (id, product_id, hierarchy_id, user_id, status) VALUES
        (1, 1, 2, 1, 'PENDING'), (2, 2, 2, 1, 'PENDING');

                     
  """)
  await db.commit()
  await cursor.close()

@pytest.mark.asyncio
async def test_get_task_by_id(db):
  await insert_data(db)
  repo = CategoryAssignmentTaskRepository(db)
  task = await repo.get_by_id(1)
  assert task.task_id == 1
  assert task.product_id == 1
  assert task.hierarchy_id == 2
  assert task.user_id == 1
  assert task.status == 'PENDING'


@pytest.mark.asyncio
async def test_get_not_existing_task_by_id(db):
  await insert_data(db)
  repo = CategoryAssignmentTaskRepository(db)
  task = await repo.get_by_id(100)
  assert task is None

@pytest.mark.asyncio
async def test_get_task_by_product_and_hierarchy(db):
  await insert_data(db)
  repo = CategoryAssignmentTaskRepository(db)
  task = await repo.get_by_product_and_hierarchy(1, 2)
  assert task.task_id == 1
  assert task.product_id == 1
  assert task.hierarchy_id == 2
  assert task.user_id == 1
  assert task.status == 'PENDING'

@pytest.mark.asyncio
async def test_get_task_by_product_and_not_existing_hierarchy(db):
  await insert_data(db)
  repo = CategoryAssignmentTaskRepository(db)
  task = await repo.get_by_product_and_hierarchy(1, 5)
  assert task is None


@pytest.mark.asyncio
async def test_update_task(db):
  await insert_data(db)
  repo = CategoryAssignmentTaskRepository(db)
  task = CategoryAssignmentTask(task_id= 1, product_id= 1, hierarchy_id= 2, user_id=1, status=CategoryAssignmentTaskStatus.CANCELLED)
  await repo.update(1, task)
  task = await repo.get_by_id(1)
  assert task.status == CategoryAssignmentTaskStatus.CANCELLED


@pytest.mark.asyncio
async def test_insert_task(db):
  await insert_data(db)
  repo = CategoryAssignmentTaskRepository(db)
  task = CategoryAssignmentTask(product_id=8, hierarchy_id= 2, user_id=2, status=CategoryAssignmentTaskStatus.PENDING)
  task_id = await repo.insert(task)
  task = await repo.get_by_id(task_id)
  assert task.product_id == 8
  assert task.hierarchy_id == 2
  assert task.user_id == 2
  assert task.status == CategoryAssignmentTaskStatus.PENDING

@pytest.mark.asyncio
async def test_delete_task(db):
  await insert_data(db)
  repo = CategoryAssignmentTaskRepository(db)
  await repo.delete(1)
  task = await repo.get_by_id(1)
  assert task is None

@pytest.mark.asyncio
async def test_insert_tasks_for_unassigned_products(db):
  await insert_data(db)
  repo = CategoryAssignmentTaskRepository(db)
  count = await repo.insert_tasks_for_unassigned_products(1, 2, 20)
  assert count == 6
  product = await repo.get_by_product_and_hierarchy(5, 2)
  assert product is not None
  
@pytest.mark.asyncio
async def test_insert_tasks_for_unassigned_products_less_limit(db):
  await insert_data(db)
  repo = CategoryAssignmentTaskRepository(db)
  count = await repo.insert_tasks_for_unassigned_products(1, 2, 3)
  assert count == 3


@pytest.mark.asyncio
async def test_delete_by_user_and_product(db):
  await insert_data(db)
  repo = CategoryAssignmentTaskRepository(db)
  count = await repo.delete_by_user_and_product(1, 2)
  assert count == 1
  task = await repo.get_by_id(2)
  assert task is None

@pytest.mark.asyncio
async def test_delete_by_user(db):
  await insert_data(db)
  repo = CategoryAssignmentTaskRepository(db)
  count = await repo.delete_by_user(1)
  assert count == 2
  task = await repo.get_by_id(2)
  assert task is None