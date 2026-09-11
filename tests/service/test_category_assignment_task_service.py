import pytest
from product_catalog_context.application.errors.errors import TaskNotFoundError, CategoryDoesNotBelongToHierarchy, CategoryHierarchyDoesNotExist, ProductNotFoundError, TaskDoesNotExist, TaskNotFoundError, TasksBelongToDifferentHierarchies, UserIdRequired
from product_catalog_context.domain.tasks.category_assignment_task_status import CategoryAssignmentTaskStatus
from product_catalog_context.domain.errors import CategoryAssignmentNotAllowed, DraftCategoryHierarchyCannotBeDeleted, CategoryHierarchyCannotBeRevertedToDraft,ParentCategoryNotInHierarchy, CategoryHierarchyIsNotDraft,CategoryHierarchyCannotBePublished, OnlyDraftHierarchyCanBeUpdated, DraftCategoryHierarchyCannotBeCreated, DraftCategoryIdCountMismatch
from product_catalog_context.application.category_assignment_task_service import CategoryAssignmentTaskService

pytestmark = pytest.mark.usefixtures('insert_data')

@pytest.mark.asyncio
async def test_get_task(category_assignment_service: CategoryAssignmentTaskService):
  task = await category_assignment_service.get_task(1)
  assert task.task_id == 1
  assert task.product_id == 2
  assert task.hierarchy_id == 2
  assert task.user_id == 1
  assert task.status == CategoryAssignmentTaskStatus.PENDING

@pytest.mark.asyncio
async def test_get_not_existing_task(category_assignment_service):
  with pytest.raises(TaskDoesNotExist):
    task = await category_assignment_service.get_task(100)

@pytest.mark.asyncio
async def test_complete_category_assignment(category_assignment_service : CategoryAssignmentTaskService, product_management_service):
  await category_assignment_service.complete_category_assignment(task_id=1, category_id=9, product_editor_id=1)
  task = await category_assignment_service.get_task(1)
  assert task.status == CategoryAssignmentTaskStatus.COMPLETED

  product = await product_management_service.get(task.product_id)
  print(product.category_assignments)
  assert 9 in[assignment.category_id for assignment in product.category_assignments.values()]

@pytest.mark.asyncio
async def test_complete_category_assignment_in_active_hierarchy(category_assignment_service, db):
  with pytest.raises(CategoryAssignmentNotAllowed):
    await category_assignment_service.complete_category_assignment(task_id=2, category_id=1, product_editor_id=3)

@pytest.mark.asyncio
async def test_assign_tasks_for_user_by_active_category_id(category_assignment_service, db):
  await category_assignment_service.assign_tasks_for_user_by_active_category_id(product_editor_id=3, hierarchy_id=2, catalog_manager_id=1, current_category_id=2, limit=20)
  cursor = await db.execute("""
  SELECT product_id, hierarchy_id, user_id, status
  FROM ProductCategoryAssignmentTask
  WHERE hierarchy_id = 2 AND user_id = 3
  ORDER BY product_id
  """)
  tasks = await cursor.fetchall()
  assert len(tasks) == 3
  assert [(row['product_id'], row['user_id']) for row in tasks] == [(4, 3), (5, 3), (8, 3)]

@pytest.mark.asyncio
async def test_assign_tasks_for_user_by_active_category_id_with_limit(category_assignment_service, db):
  await category_assignment_service.assign_tasks_for_user_by_active_category_id(product_editor_id=3, catalog_manager_id=1,hierarchy_id=2, current_category_id=2, limit=1)
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
  await category_assignment_service.assign_tasks_for_users(product_editor_ids=[2, 3], hierarchy_id=2, catalog_manager_id=1)
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
  assert len(tasks_user_2) == 3


@pytest.mark.asyncio
async def test_delete_task(category_assignment_service, db):
  await category_assignment_service.delete_task(task_id=1, catalog_manager_id=1)
  with pytest.raises(TaskDoesNotExist):
    task = await category_assignment_service.get_task(1)

@pytest.mark.asyncio
async def test_not_existing_delete_task(category_assignment_service, db):
  with pytest.raises(TaskNotFoundError):
    await category_assignment_service.delete_task(task_id=1000, catalog_manager_id=1)

@pytest.mark.asyncio
async def test_delete_tasks_by_user(category_assignment_service, db):
  await category_assignment_service.delete_tasks_by_user(user_id=1, catalog_manager_id=1)
  with pytest.raises(TaskDoesNotExist):
    task = await category_assignment_service.get_task(1)


@pytest.mark.asyncio
async def test_delete_task_by_user_and_product(category_assignment_service, db):
  await category_assignment_service.delete_task_by_user_and_product(user_id=1, product_id=2, catalog_manager_id=1)
  with pytest.raises(TaskDoesNotExist):
    task = await category_assignment_service.get_task(1)

@pytest.mark.asyncio
async def test_delete_not_existing_task_by_user_and_product(category_assignment_service, db):
  with pytest.raises(TaskNotFoundError):
    await category_assignment_service.delete_task_by_user_and_product(user_id=1, product_id=100, catalog_manager_id=1)