from abc import ABC, abstractmethod
import asyncio

from product_catalog_context.infrastructure.outbox.repository import OutboxDAO


class MessageOutboxDispatcher(ABC):
  def __init__(self, session_factory, test, sync=False):
    self.session_factory = session_factory
    self.test = test
    self.sync = sync
  @abstractmethod
  async def pull_messages(self):
    pass

  @abstractmethod
  async def handle(self, message_id):
    pass

  async def _handle_errors(self, message_id, e):
    print('ERROR OCCURRED')
    print(type(e))
    print(repr(e))
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
      if not self.sync:
        tasks = [self.handle(message_id) for message_id in unprocessed_message_ids]
        await asyncio.gather(*tasks)
      else:
        for message_id in unprocessed_message_ids:
          await self.handle(message_id)
      if self.test:
        return