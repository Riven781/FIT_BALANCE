import pytest
from product_catalog_context.domain.tasks.category_assignment_task_repository import CategoryAssignmentTaskRepository
from product_catalog_context.domain.tasks.category_assignment_task_status import CategoryAssignmentTaskStatus
from product_catalog_context.domain.tasks.category_assignment_task import CategoryAssignmentTask


pytestmark = pytest.mark.usefixtures('insert_data')

@pytest.mark.asyncio
async def test_get_by_id(category_assignment_task_repository: CategoryAssignmentTaskRepository):
  task = await category_assignment_task_repository.get_by_id(1)
  assert task.task_id == 1
  assert task.hierarchy_id == 3
  assert task.product_id == 2
  assert task.status == CategoryAssignmentTaskStatus.PENDING

@pytest.mark.asyncio
async def test_get_by_product_and_hierarchy(category_assignment_task_repository: CategoryAssignmentTaskRepository):
  task = await category_assignment_task_repository.get_by_product_and_hierarchy(2, 3)
  assert task.task_id == 1
  assert task.hierarchy_id == 3
  assert task.product_id == 2
  assert task.status == CategoryAssignmentTaskStatus.PENDING

@pytest.mark.asyncio
async def test_insert_tasks_for_unassigned_products(category_assignment_task_repository: CategoryAssignmentTaskRepository):
  rowcount = await category_assignment_task_repository.insert_tasks_for_unassigned_products(user_id=1, hierarchy_id=2, limit=20)
  assert rowcount == 7
  assert await category_assignment_task_repository.get_by_product_and_hierarchy(2, 2) is not None
  assert await category_assignment_task_repository.get_by_product_and_hierarchy(3, 2) is not None
  task = await category_assignment_task_repository.get_by_product_and_hierarchy(4, 2)
  assert task.product_id == 4
  assert task.hierarchy_id == 2
  assert task.status == CategoryAssignmentTaskStatus.PENDING

@pytest.mark.asyncio
async def test_delete(category_assignment_task_repository: CategoryAssignmentTaskRepository, db_session):
  task = await category_assignment_task_repository.get_by_id(task_id=1)
  await category_assignment_task_repository.delete(task)
  await db_session.flush()
  task = await category_assignment_task_repository.get_by_id(task_id=1)
  assert task is None

@pytest.mark.asyncio
async def test_delete_by_user(category_assignment_task_repository: CategoryAssignmentTaskRepository):
  count = await category_assignment_task_repository.delete_by_user(user_id=1)
  task = await category_assignment_task_repository.get_by_id(task_id=1)
  assert task is None
  assert count == 1

@pytest.mark.asyncio
async def test_delete_by_hierarchy(category_assignment_task_repository: CategoryAssignmentTaskRepository):
  await category_assignment_task_repository.delete_by_hierarchy(hierarchy_id=3)
  task = await category_assignment_task_repository.get_by_id(task_id=1)
  assert task is None

@pytest.mark.asyncio
async def test_delete_by_user_and_product(category_assignment_task_repository: CategoryAssignmentTaskRepository):
  count = await category_assignment_task_repository.delete_by_user_and_product(user_id=1, product_id=2)
  task = await category_assignment_task_repository.get_by_id(task_id=1)
  assert task is None
  assert count == 1

@pytest.mark.asyncio
async def test_save_new_task(category_assignment_task_repository: CategoryAssignmentTaskRepository):
  new_task = CategoryAssignmentTask(product_id=4, hierarchy_id=3, user_id=2, status=CategoryAssignmentTaskStatus.COMPLETED)
  await category_assignment_task_repository.save(new_task)
  task = await category_assignment_task_repository.get_by_id(task_id=new_task.task_id)
  assert task.hierarchy_id == 3
  assert task.product_id == 4
  assert task.status == CategoryAssignmentTaskStatus.COMPLETED
  assert task.user_id == 2


@pytest.mark.asyncio
async def test_save_existing_task(category_assignment_task_repository: CategoryAssignmentTaskRepository):
  task = await category_assignment_task_repository.get_by_id(1)
  task.complete()
  await category_assignment_task_repository.save(task)
  updated_task = await category_assignment_task_repository.get_by_id(task_id=1)
  assert task.hierarchy_id == 3
  assert task.product_id == 2
  assert updated_task.status == CategoryAssignmentTaskStatus.COMPLETED
  assert updated_task.user_id == 1

@pytest.mark.asyncio
async def test_insert_all(category_assignment_task_repository: CategoryAssignmentTaskRepository):
  await category_assignment_task_repository.insert_all([
    CategoryAssignmentTask(product_id=4, hierarchy_id=1, user_id=10, status=CategoryAssignmentTaskStatus.PENDING),
    CategoryAssignmentTask(product_id=5, hierarchy_id=1, user_id=10, status=CategoryAssignmentTaskStatus.COMPLETED),
  ])
  task_1 = await category_assignment_task_repository.get_by_product_and_hierarchy(4, 1)
  assert task_1.user_id == 10
  assert task_1.status == CategoryAssignmentTaskStatus.PENDING
  task_2 = await category_assignment_task_repository.get_by_product_and_hierarchy(5, 1)
  assert task_2.user_id == 10
  assert task_2.status == CategoryAssignmentTaskStatus.COMPLETED
