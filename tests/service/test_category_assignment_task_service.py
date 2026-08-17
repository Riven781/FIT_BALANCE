import pytest
from product_catalog_context.application.errors.errors import TaskNotFoundError, CategoryDoesNotBelongToHierarchy, CategoryHierarchyDoesNotExist, ProductNotFoundError, TaskDoesNotExist, TaskNotFoundError, TasksBelongToDifferentHierarchies, UserIdRequired
from product_catalog_context.domain.enums.category_assignment_task_status import CategoryAssignmentTaskStatus
from product_catalog_context.domain.errors import CategoryAssignmentNotAllowed, DraftCategoryHierarchyCannotBeDeleted, CategoryHierarchyCannotBeRevertedToDraft,ParentCategoryNotInHierarchy, CategoryHierarchyIsNotDraft,CategoryHierarchyCannotBePublished, OnlyDraftHierarchyCanBeUpdated, DraftCategoryHierarchyCannotBeCreated, DraftCategoryIdCountMismatch


async def insert_data(db):
  cursor = await db.executescript(""" 
    INSERT INTO ProductCategoryHierarchy (id, status) VALUES
      (2, "PLANNED_FOR_PUBLICATION");
    INSERT INTO ProductCategoryHierarchy (id, status) VALUES
      (1, "ACTIVE");
    INSERT INTO ProductCategoryNode (id, name, parent_id, hierarchy_id, source_node_id) VALUES
      (10, "Produkty", NULL, 2, 1),
      (11, "Roślinnopodobne", 10, 2, 2),
      (12, "Zwierzęce", 10, 2, 3),
      (13, "Schabik", 12, 2, 4),
      (14, "Boczek", 12, 2, 5),
      (15, "Tofu", 11, 2, 6),
      (16, "Groszek", 11, 2, 7),
      (17, "Groszek Zielony", 16, 2, NULL),
      (18, "Boczek Pikantny", 14, 2, NULL),
      
      (1, 'Wszystko', NULL, 1, NULL),
      (2, 'Roślinne', 1, 1, NULL),
      (3, 'Zwierzęce', 1, 1, NULL),
      (4, 'Schab', 3, 1, NULL),
      (5, 'Boczek', 3, 1, NULL),
      (6, 'Tofu', 2, 1, NULL),
      (7, 'Groszek', 2, 1, NULL);
  
    INSERT INTO User(id, username, email, hashed_password) VALUES 
      (1, 'ZYZ','xyz@gm.c','xyz'), 
      (2, 'ABC','abc@gm.c','abc'),
      (3, 'OKO','oko@gm.c','oko');

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

    INSERT INTO ProductCategoryAssignment (product_id, node_id) VALUES
    (1, 4), (2, 4), (3, 4), (4, 6), (6, 5), (7, 5);

    INSERT INTO ProductCategoryAssignmentTask (id, product_id, hierarchy_id, user_id, status) VALUES
      (1, 1, 2, 1, 'PENDING'), (2, 1, 1, 1, 'PENDING');


  """)
  await db.commit()
  await cursor.close()

@pytest.mark.asyncio
async def test_get_task(category_assignment_service, db):
  await insert_data(db)
  task = await category_assignment_service.get_task(1)
  assert task.task_id == 1
  assert task.product_id == 1
  assert task.hierarchy_id == 2
  assert task.user_id == 1
  assert task.status == CategoryAssignmentTaskStatus.PENDING

@pytest.mark.asyncio
async def test_get_not_existing_task(category_assignment_service):
  with pytest.raises(TaskDoesNotExist):
    task = await category_assignment_service.get_task(100)

@pytest.mark.asyncio
async def test_complete_category_assignment(category_assignment_service, db, product_management_service):
  await insert_data(db)
  await category_assignment_service.complete_category_assignment(1, 13)
  task = await category_assignment_service.get_task(1)
  assert task.status == CategoryAssignmentTaskStatus.COMPLETED

  product = await product_management_service.get(task.product_id)
  assert product.planned_category_id == 13

@pytest.mark.asyncio
async def test_complete_category_assignment_in_active_hierarchy(category_assignment_service, db):
  await insert_data(db)
  with pytest.raises(CategoryAssignmentNotAllowed):
    await category_assignment_service.complete_category_assignment(2, 1)

@pytest.mark.asyncio
async def test_assign_tasks_for_user_by_active_category_id(category_assignment_service, db):
  await insert_data(db)
  await category_assignment_service.assign_tasks_for_user_by_active_category_id(user_id=3, hierarchy_id=2, current_category_id=4, limit=20)
  cursor = await db.execute("""
  SELECT product_id, hierarchy_id, user_id, status
  FROM ProductCategoryAssignmentTask
  WHERE hierarchy_id = 2 AND user_id = 3
  ORDER BY product_id
  """)
  tasks = await cursor.fetchall()
  assert len(tasks) == 2
  assert [(row['product_id'], row['user_id']) for row in tasks] == [(2, 3), (3, 3)]

@pytest.mark.asyncio
async def test_assign_tasks_for_user_by_active_category_id_with_limit(category_assignment_service, db):
  await insert_data(db)
  await category_assignment_service.assign_tasks_for_user_by_active_category_id(user_id=3, hierarchy_id=2, current_category_id=4, limit=1)
  cursor = await db.execute("""
  SELECT product_id, hierarchy_id, user_id, status
  FROM ProductCategoryAssignmentTask
  WHERE hierarchy_id = 2 AND user_id = 3
  ORDER BY product_id
  """)
  tasks = await cursor.fetchall()
  assert len(tasks) == 1

@pytest.mark.asyncio
async def test_assign_tasks_for_users(category_assignment_service, db):
  await insert_data(db)
  await category_assignment_service.assign_tasks_for_users([2, 3], 2)
  cursor = await db.execute("""
    SELECT product_id, hierarchy_id, user_id, status
    FROM ProductCategoryAssignmentTask
    WHERE hierarchy_id = 2 AND user_id = 3
    ORDER BY product_id
    """)
  tasks_user_3 = await cursor.fetchall()
  assert len(tasks_user_3) == 3

  cursor = await db.execute("""
    SELECT product_id, hierarchy_id, user_id, status
    FROM ProductCategoryAssignmentTask
    WHERE hierarchy_id = 2 AND user_id = 2
    ORDER BY product_id
    """)
  tasks_user_2 = await cursor.fetchall()
  assert len(tasks_user_2) == 4


@pytest.mark.asyncio
async def test_delete_task(category_assignment_service, db):
  await insert_data(db)
  await category_assignment_service.delete_task(1)
  with pytest.raises(TaskDoesNotExist):
    task = await category_assignment_service.get_task(1)

@pytest.mark.asyncio
async def test_not_existing_delete_task(category_assignment_service, db):
  await insert_data(db)
  with pytest.raises(TaskNotFoundError):
    await category_assignment_service.delete_task(1000)

@pytest.mark.asyncio
async def test_delete_tasks_by_user(category_assignment_service, db):
  await insert_data(db)
  await category_assignment_service.delete_tasks_by_user(1)
  with pytest.raises(TaskDoesNotExist):
    task = await category_assignment_service.get_task(1)
  with pytest.raises(TaskDoesNotExist):
    task = await category_assignment_service.get_task(2)

@pytest.mark.asyncio
async def test_delete_task_by_user_and_product(category_assignment_service, db):
  await insert_data(db)
  await category_assignment_service.delete_task_by_user_and_product(1, 1)
  with pytest.raises(TaskDoesNotExist):
    task = await category_assignment_service.get_task(1)

@pytest.mark.asyncio
async def test_delete_not_existing_task_by_user_and_product(category_assignment_service, db):
  await insert_data(db)
  with pytest.raises(TaskNotFoundError):
    await category_assignment_service.delete_task_by_user_and_product(1, 100)
  