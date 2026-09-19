from product_catalog_context.domain.messages.command_bus import CommandBus
from product_catalog_context.domain.messages.message_serializer import MessageSerializer
from product_catalog_context.infrastructure.outbox.message_dispatcher import MessageOutboxDispatcher
from product_catalog_context.infrastructure.outbox.repository import OutboxDAO
import asyncio


class OutboxCommandDispatcher(MessageOutboxDispatcher):
  def __init__(self, session_factory, command_bus: CommandBus, message_serializer: MessageSerializer, test = False):
    super().__init__(session_factory, test)
    self.command_bus = command_bus
    self.message_serializer = message_serializer

  async def pull_messages(self):
    async with self.session_factory() as session:
      outbox_dao = OutboxDAO(session)
      unprocessed_message_ids = await outbox_dao.get_unprocessed_command_ids(limit=50)
      return unprocessed_message_ids

  async def handle(self, message_id):
    try:
      async with self.session_factory() as session:
        outbox_repository = OutboxDAO(session=session)
        message = await outbox_repository.get_by_id(message_id)
      message = self.message_serializer.deserialize(message_name=message.message_name, payload=message.payload)
      self.command_bus.dispatch(message)
    except Exception as e:
      await self._handle_errors(message_id=message_id, e=e)
      return
    await self._process_message(message_id)
