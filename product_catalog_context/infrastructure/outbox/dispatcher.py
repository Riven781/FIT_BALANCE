import json
import asyncio
from product_catalog_context.domain.messages.command_bus import CommandBus
from product_catalog_context.domain.messages.event_bus import EventBus
from product_catalog_context.domain.messages.message_serializer import MessageSerializer
from product_catalog_context.infrastructure.outbox.repository import OutboxDAO
from product_catalog_context.infrastructure.sql_alchemy_repository.unit_of_work import SqlAlchemyUnitOfWork


class OutboxDispatcher:
  def __init__(self, session_factory, event_bus: EventBus, command_bus: CommandBus, message_serializer: MessageSerializer, test=None):
    self.session_factory = session_factory
    self.event_bus = event_bus
    self.command_bus = command_bus
    self.message_serializer = message_serializer
    self.test = test

  async def pull_messages(self):
    async with self.session_factory() as session:
      outbox_dao = OutboxDAO(session)
      unprocessed_message_ids = await outbox_dao.get_unprocessed_message_ids(limit=50)
      return unprocessed_message_ids


  async def handle(self, message_id):
    try:
      async with self.session_factory() as session:
        outbox_repository = OutboxDAO(session=session)
        message = await outbox_repository.get_by_id(message_id)
      message = self.message_serializer.deserialize(message_name=message.message_name, payload=message.payload)

      if message.message_type == 'event':
        self.event_bus.publish(message)
      if message.message_type == 'command':
        self.command_bus.dispatch(message)

    except Exception as e:
      await self._handle_errors(message_id=message_id, e=e)
      return
    await self._process_message(message_id)

  async def _handle_errors(self, message_id, e):
    print('ERROR')
    print(e)
    async with self.session_factory() as session:
      outbox_repository = OutboxDAO(session=session)
      await outbox_repository.increase_retry_count(message_id)
      await session.commit()

  async def _process_message(self, message_id):
    async with self.session_factory() as session:
      outbox_repository = OutboxDAO(session=session)
      await outbox_repository.mark_as_processed(message_id)
      await session.commit()

  async def run(self):
    while True:
      unprocessed_message_ids = await self.pull_messages()
      print(unprocessed_message_ids)
      if not unprocessed_message_ids:
        if self.test:
          return
        await asyncio.sleep(1)
        continue
      tasks = [self.handle(message_id) for message_id in unprocessed_message_ids]
      await asyncio.gather(*tasks)
      if self.test:
        return
