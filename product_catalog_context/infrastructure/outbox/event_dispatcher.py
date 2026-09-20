import argparse
import asyncio

from product_catalog_context.application.handlers.product_data_changed_handler import ProductDataChangedHandler
from product_catalog_context.application.handlers.product_issue_confirmed_handler import ProductIssueConfirmedHandler
from product_catalog_context.domain.issues.product_issue_confirmed import ProductIssueConfirmed
from product_catalog_context.domain.messages.event_bus import EventBus
from product_catalog_context.domain.messages.message_registry import MessageRegistry
from product_catalog_context.domain.messages.message_serializer import MessageSerializer
from product_catalog_context.domain.product.events import ProductDataChanged
from product_catalog_context.infrastructure.outbox.message_dispatcher import MessageOutboxDispatcher
from product_catalog_context.infrastructure.outbox.repository import OutboxDAO
from product_catalog_context.infrastructure.outbox.test_session_factory import get_session_factory
from product_catalog_context.infrastructure.sql_alchemy_repository.unit_of_work import SqlAlchemyUnitOfWork, SqlAlchemyUnitOfWorkFactory
#python -m product_catalog_context.infrastructure.outbox.event_dispatcher
class OutboxEventDispatcher(MessageOutboxDispatcher):
  def __init__(self, session_factory, event_bus: EventBus, message_serializer: MessageSerializer, test=False):
    super().__init__(session_factory, test)
    self.event_bus = event_bus
    self.message_serializer = message_serializer

  async def pull_messages(self):
    async with self.session_factory() as session:
      outbox_dao = OutboxDAO(session)
      unprocessed_message_ids = await outbox_dao.get_unprocessed_event_ids(limit=50)
      return unprocessed_message_ids

  async def handle(self, message_id):
    try:
      async with self.session_factory() as session:
        outbox_repository = OutboxDAO(session=session)
        message = await outbox_repository.get_by_id(message_id)
      event = self.message_serializer.deserialize(message_name=message.message_name, payload=message.payload)
      print(event)
      await self.event_bus.publish(event)
    except Exception as e:
      await self._handle_errors(message_id=message_id, e=e)
      return
    await self._process_message(message_id)

def parse_args():
  parser = argparse.ArgumentParser()
  parser.add_argument('--database-url', required=True)
  return parser.parse_args()

if __name__ == '__main__':
  args = parse_args()
  event_bus = EventBus()
  event_bus.subscribe(ProductIssueConfirmed, ProductIssueConfirmedHandler(SqlAlchemyUnitOfWorkFactory(get_session_factory(args.database_url))))
  event_bus.subscribe(ProductDataChanged, ProductDataChangedHandler(SqlAlchemyUnitOfWorkFactory(get_session_factory(args.database_url))))

  registry = MessageRegistry()
  registry.register('product_issue_confirmed', ProductIssueConfirmed)
  registry.register(ProductDataChanged.event_type, ProductDataChanged)

  dispatcher = OutboxEventDispatcher(get_session_factory(args.database_url), event_bus, MessageSerializer(registry))
  asyncio.run(dispatcher.run())