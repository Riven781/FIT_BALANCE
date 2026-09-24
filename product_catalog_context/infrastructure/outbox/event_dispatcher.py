import argparse
import asyncio

from product_catalog_context.application.handlers.delete_category_assignment_tasks import DeleteCategoryAssignmentTasks
from product_catalog_context.application.handlers.mark_affected_product_issue_as_obsolete import MarkAffectedProductIssueAsObsolete
from product_catalog_context.application.handlers.apply_resolved_value_to_product import ApplyResolvedValueToProduct
from product_catalog_context.application.handlers.resolve_category_assignment_task import ResolveCategoryAssignmentTask
from product_catalog_context.application.product_issue_confirmation.product_issue_confirmation_saga_service import ProductIssueConfirmationSagaService
from product_catalog_context.domain.category_hierarchy.events import ProductCategoryHierarchyPublished, ProductCategoryHierarchyRevertedToDraft
from product_catalog_context.domain.issues.events import MessageExecutionFailed, ProductIssueConfirmationCancelledAsObsolete, ProductIssueConfirmationStarted, ProductIssueConfirmed, ProductIssueResetToPending, ResolvedValueAppliedToProduct
from product_catalog_context.domain.messages.domain_message_publisher import DomainMessagePublisher
from product_catalog_context.domain.messages.event_bus import EventBus
from product_catalog_context.domain.messages.message_registry import MessageRegistry
from product_catalog_context.domain.messages.message_serializer import MessageSerializer
from product_catalog_context.domain.product.events import ProductCategoryChangedInHierarchy, ProductDataChanged, ResolvedValueApplicationRejected
from product_catalog_context.domain.repository.errors import ConcurrentModification
from product_catalog_context.infrastructure.outbox.dispatcher import OutboxDispatcher
from product_catalog_context.infrastructure.outbox.message_dispatcher import MessageOutboxDispatcher
from product_catalog_context.infrastructure.outbox.message_writer import SqlAlchemyOutboxMessageWriter
from product_catalog_context.infrastructure.outbox.model import OutboxMessage
from product_catalog_context.infrastructure.outbox.repository import OutboxDAO
from product_catalog_context.infrastructure.outbox.subscriber import DoubleOutboxSubscriber, OutboxSubscriber
from product_catalog_context.infrastructure.outbox.test_session_factory import get_session_factory
from product_catalog_context.infrastructure.sql_alchemy_repository.unit_of_work import SqlAlchemyUnitOfWork, SqlAlchemyUnitOfWorkFactory
from datetime import datetime, timezone

#python -m product_catalog_context.infrastructure.outbox.event_dispatcher
class OutboxEventDispatcher(MessageOutboxDispatcher):
  def __init__(self, session_factory, event_bus: EventBus, message_serializer: MessageSerializer, test=False, sync=False):
    super().__init__(session_factory, test, sync)
    self.event_bus = event_bus
    self.message_serializer = message_serializer

  async def pull_messages(self):
    async with self.session_factory() as session:
      outbox_dao = OutboxDAO(session)
      unprocessed_message_ids = await outbox_dao.get_unprocessed_event_ids(limit=50)
      return unprocessed_message_ids

  async def _send_message_failed(self, e, retry_count, deserialized_message):
    if retry_count < 4:
      return
    message = None
    if isinstance(e, ConcurrentModification):#saga type soon
      message = MessageExecutionFailed(message_type='event', message_name=deserialized_message.event_type, saga_id=deserialized_message.saga_id, error_type='concurrent_modification')
      #outbox_message = OutboxMessage(message_type='event', message_name=MessageExecutionFailed.event_type, payload=self.message_serializer.serialize(message), occurred_at=datetime.now(timezone.utc))

    if message is None:
      return
    async with self.session_factory() as session:
      writer = SqlAlchemyOutboxMessageWriter(session)
      await writer.write(message)
      await session.commit()

      

  async def handle(self, message_id):
    try:
      async with self.session_factory() as session:
        outbox_repository = OutboxDAO(session=session)
        outbox_message = await outbox_repository.get_by_id(message_id)
      event = self.message_serializer.deserialize(message_name=outbox_message.message_name, payload=outbox_message.payload)
      #print(f'Handle event: {message_id}: {event}')

      await self.event_bus.publish(event)
    except Exception as e:
      await self._send_message_failed(e, outbox_message.retry_count, event)
      await self._handle_errors(message_id=message_id, e=e)
      return
    await self._process_message(message_id)


def parse_args():
  parser = argparse.ArgumentParser()
  parser.add_argument('--database-url', required=True)
  parser.add_argument('--double-message', action="store_true")

  return parser.parse_args()

if __name__ == '__main__':
  args = parse_args()
  if args.double_message:
    subscriber = DoubleOutboxSubscriber()
  else:
    subscriber = OutboxSubscriber()
  publisher = DomainMessagePublisher()
  publisher.global_subscribe(subscriber)

  event_bus = EventBus()
  
  #event_bus.subscribe(ProductIssueConfirmed, ApplyResolvedValueToProduct(SqlAlchemyUnitOfWorkFactory(get_session_factory(args.database_url))))
  event_bus.subscribe(ProductDataChanged, MarkAffectedProductIssueAsObsolete(SqlAlchemyUnitOfWorkFactory(get_session_factory(args.database_url))))
  event_bus.subscribe(ProductCategoryHierarchyPublished, DeleteCategoryAssignmentTasks(SqlAlchemyUnitOfWorkFactory(get_session_factory(args.database_url))))
  event_bus.subscribe(ProductCategoryHierarchyRevertedToDraft, DeleteCategoryAssignmentTasks(SqlAlchemyUnitOfWorkFactory(get_session_factory(args.database_url))))
  event_bus.subscribe(ProductCategoryChangedInHierarchy, ResolveCategoryAssignmentTask(SqlAlchemyUnitOfWorkFactory(get_session_factory(args.database_url))))

  session_factory = get_session_factory(args.database_url)
  unit_of_work_factory = SqlAlchemyUnitOfWorkFactory(session_factory)
  product_issue_confirmation_saga = ProductIssueConfirmationSagaService(publisher, unit_of_work_factory)
  event_bus.subscribe(ProductIssueConfirmationStarted, product_issue_confirmation_saga)
  event_bus.subscribe(ResolvedValueAppliedToProduct, product_issue_confirmation_saga)
  event_bus.subscribe(ResolvedValueApplicationRejected, product_issue_confirmation_saga)
  event_bus.subscribe(ProductIssueConfirmed, product_issue_confirmation_saga)
  event_bus.subscribe(ProductIssueConfirmationCancelledAsObsolete, product_issue_confirmation_saga)
  event_bus.subscribe(MessageExecutionFailed, product_issue_confirmation_saga)  #router w przyszłości
  event_bus.subscribe(ProductIssueResetToPending, product_issue_confirmation_saga)
  event_bus.subscribe(MessageExecutionFailed, product_issue_confirmation_saga)



  registry = MessageRegistry()
  #registry.register('product_issue_confirmed', ProductIssueConfirmed)
  registry.register(ProductDataChanged.event_type, ProductDataChanged)
  registry.register(ProductCategoryHierarchyPublished.event_type, ProductCategoryHierarchyPublished)
  registry.register(ProductCategoryHierarchyRevertedToDraft.event_type, ProductCategoryHierarchyRevertedToDraft)
  registry.register(ProductCategoryChangedInHierarchy.event_type, ProductCategoryChangedInHierarchy)


  registry.register(ProductIssueConfirmationStarted.event_type, ProductIssueConfirmationStarted)
  registry.register(ResolvedValueAppliedToProduct.event_type, ResolvedValueAppliedToProduct)
  registry.register(ResolvedValueApplicationRejected.event_type, ResolvedValueApplicationRejected)
  registry.register(ProductIssueConfirmed.event_type, ProductIssueConfirmed)
  registry.register(ProductIssueConfirmationCancelledAsObsolete.event_type, ProductIssueConfirmationCancelledAsObsolete)
  registry.register(MessageExecutionFailed.event_type, MessageExecutionFailed)
  registry.register(ProductIssueResetToPending.event_type, ProductIssueResetToPending)
  registry.register(MessageExecutionFailed.event_type, MessageExecutionFailed)


  dispatcher = OutboxEventDispatcher(get_session_factory(args.database_url), event_bus, MessageSerializer(registry), sync=False)
  asyncio.run(dispatcher.run())