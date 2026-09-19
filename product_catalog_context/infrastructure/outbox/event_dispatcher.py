from product_catalog_context.domain.messages.event_bus import EventBus
from product_catalog_context.domain.messages.message_serializer import MessageSerializer
from product_catalog_context.infrastructure.outbox.message_dispatcher import MessageOutboxDispatcher
from product_catalog_context.infrastructure.outbox.repository import OutboxDAO


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
      await self.event_bus.publish(event)
    except Exception as e:
      await self._handle_errors(message_id=message_id, e=e)
      return
    await self._process_message(message_id)
