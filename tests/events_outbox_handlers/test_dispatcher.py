import pytest

from product_catalog_context.application.handlers.delete_category_assignment_tasks import DeleteCategoryAssignmentTasks
from product_catalog_context.domain.category_hierarchy.events import ProductCategoryHierarchyRevertedToDraft
from product_catalog_context.domain.tasks.category_assignment_task_repository import CategoryAssignmentTaskRepository
from product_catalog_context.infrastructure.outbox.one_event_dispatcher import OutboxEventDispatcherPerEvent
from product_catalog_context.infrastructure.outbox.event_dispatcher import OutboxEventDispatcher

from product_catalog_context.infrastructure.outbox.subscriber import OutboxSubscriber
from product_catalog_context.infrastructure.outbox.repository import OutboxDAO

pytestmark = pytest.mark.usefixtures('insert_data')
#pytest tests/events_outbox_handlers
@pytest.mark.asyncio
async def test_one_event(
  db_session,
  session_factory, 
  category_assignment_task_repository: CategoryAssignmentTaskRepository, 
  outbox_subscriber: OutboxSubscriber,
  outbox_dao: OutboxDAO
):
  dispatcher = OutboxEventDispatcherPerEvent(
    session_factory, 
    'product_category_hierarchy_reverted_to_draft',
    DeleteCategoryAssignmentTasks,
    ProductCategoryHierarchyRevertedToDraft, test=True)
  await outbox_subscriber.handle(
    ProductCategoryHierarchyRevertedToDraft(hierarchy_id=3)
  )
  await db_session.commit()
  assert await category_assignment_task_repository.get_total_in_hierarchy(3) == 2
  await dispatcher.run()
  assert await category_assignment_task_repository.get_total_in_hierarchy(3) == 0
  outbox = await outbox_dao.get_by_id(1)
  assert outbox.processed_at is not None
  assert outbox.retry_count == 0

@pytest.mark.asyncio
async def test_one_event2(
  db_session,
  outbox_event_dispatcher: OutboxEventDispatcher, 
  category_assignment_task_repository: CategoryAssignmentTaskRepository, 
  outbox_subscriber: OutboxSubscriber,
  outbox_dao: OutboxDAO
):
  await outbox_subscriber.handle(
    ProductCategoryHierarchyRevertedToDraft(hierarchy_id=3)
  )
  await db_session.commit()
  assert await category_assignment_task_repository.get_total_in_hierarchy(3) == 2
  await outbox_event_dispatcher.run()
  assert await category_assignment_task_repository.get_total_in_hierarchy(3) == 0
  outbox = await outbox_dao.get_by_id(1)
  assert outbox.processed_at is not None
  assert outbox.retry_count == 0