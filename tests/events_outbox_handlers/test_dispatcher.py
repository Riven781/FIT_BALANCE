import pytest

from product_catalog_context.application.handlers.category_hierarchy_published_or_reverted_handler import CategoryHierarchyPublishedOrRevertedHandler
from product_catalog_context.domain.category_hierarchy.events import ProductCategoryHierarchyRevertedToDraft
from product_catalog_context.domain.tasks.category_assignment_task_repository import CategoryAssignmentTaskRepository
from product_catalog_context.infrastructure.outbox.dispatcher import OutboxEventDispatcher
from product_catalog_context.infrastructure.outbox.subscriber import OutboxSubscriber
from product_catalog_context.infrastructure.outbox.repository import OutboxDAO

pytestmark = pytest.mark.usefixtures('insert_data')

@pytest.mark.asyncio
async def test_one_event(
  db_session,
  session_factory, 
  category_assignment_task_repository: CategoryAssignmentTaskRepository, 
  outbox_subscriber: OutboxSubscriber,
  outbox_dao: OutboxDAO):
  dispatcher = OutboxEventDispatcher(
    session_factory, 
    'product_category_hierarchy_reverted_to_draft',
    CategoryHierarchyPublishedOrRevertedHandler,
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
  assert outbox.attempts == 0