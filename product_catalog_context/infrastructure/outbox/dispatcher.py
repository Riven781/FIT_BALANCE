import argparse
import json
import sys
import asyncio
from product_catalog_context.application.category_hierarchy_published_or_reverted_handler import CategoryHierarchyPublishedOrRevertedHandler
from product_catalog_context.application.product_category_changed_handler import ProductCategoryChangedHandler
from product_catalog_context.application.product_data_changed_handler import ProductDataChangedHandler
from product_catalog_context.application.product_issue_confirmed_handler import ProductIssueConfirmedHandler
from product_catalog_context.domain.category_hierarchy.events import ProductCategoryHierarchyPublished, ProductCategoryHierarchyRevertedToDraft
from product_catalog_context.domain.issues.product_issue_confirmed import ProductIssueConfirmed
from product_catalog_context.domain.product.events import ProductCategoryChangedInHierarchy, ProductDataChanged
from product_catalog_context.infrastructure.outbox.repository import OutboxDAO
from product_catalog_context.infrastructure.sql_alchemy_repository.unit_of_work import SqlAlchemyUnitOfWork

from shared.database.session import get_session, session_factory
#eariel add events in outbox.py:    python shared/database/outbox.py    
#python -m product_catalog_context.infrastructure.outbox.dispatcher product_category_changed_in_hierarchy
handler_by_event_type = {
  'product_category_hierarchy_published': CategoryHierarchyPublishedOrRevertedHandler,
  'product_category_hierarchy_reverted_to_draft': CategoryHierarchyPublishedOrRevertedHandler,
  'product_category_changed_in_hierarchy' : ProductCategoryChangedHandler,
  'product_data_changed' : ProductDataChangedHandler,
  'product_issue_confirmed': ProductIssueConfirmedHandler
}

event_by_type = {
  'product_category_hierarchy_published' : ProductCategoryHierarchyPublished,
  'product_category_hierarchy_reverted_to_draft' : ProductCategoryHierarchyRevertedToDraft,
  'product_category_changed_in_hierarchy' : ProductCategoryChangedInHierarchy,
  'product_data_changed' : ProductDataChanged,
  'product_issue_confirmed' : ProductIssueConfirmed
}

def get_args():
  parser = argparse.ArgumentParser()
  parser.add_argument("event_type")
  return parser.parse_args()


class OutboxEventDispatcher:
  def __init__(self, session_factory, event_type, handler_class, event_class, test=False):
    self.session_factory = session_factory
    self.event_type = event_type
    self.handler_class = handler_class
    self.event_class = event_class
    self.test = test

  async def pull_messages(self):
    async with self.session_factory() as session:
      outbox_repository = OutboxDAO(session=session)
      unprocessed_message_ids = await outbox_repository.get_unprocessed_message_ids(event_type=self.event_type, limit=50)
      return unprocessed_message_ids
    
  def _deserialize_event(self, payload, event_class):
    event_dict = json.loads(payload)
    #event_dict.pop('event_type')
    event = event_class(**event_dict)
    return event

  async def handle(self, message_id):
    try:
      async with self.session_factory() as session:
        outbox_repository = OutboxDAO(session=session)
        message = await outbox_repository.get_by_id(message_id)
        event = self._deserialize_event(payload=message.payload, event_class=self.event_class)
        uow = SqlAlchemyUnitOfWork(session)
        handler = self.handler_class(uow)
        await handler.handle(event)
    except Exception as e:
      await self._handle_errors(message_id=message_id, e=e)
      return
    await self._process_message(message_id)


  async def _process_message(self, message_id):
    async with self.session_factory() as session:
      outbox_repository = OutboxDAO(session=session)
      await outbox_repository.mark_as_processed(message_id)
      await session.commit()

  async def _handle_errors(self, message_id, e):
    print('ERROR')
    print(e)
    async with self.session_factory() as session:
      outbox_repository = OutboxDAO(session=session)
      await outbox_repository.increase_attempt(message_id)
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



async def main():
  args = get_args()
  print(f'Listen to events: {args.event_type}')

  handler_class = handler_by_event_type.get(args.event_type)
  event_class = event_by_type.get(args.event_type)

  dispatcher = OutboxEventDispatcher(session_factory, args.event_type, handler_class, event_class)

  await dispatcher.run()
  

if __name__ == '__main__':
  asyncio.run(main())