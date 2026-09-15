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

async def handle_errors(message_id, e):
  print(e)
  async with session_factory() as session:
    outbox_repository = OutboxDAO(session=session)
    await outbox_repository.increase_attempt(message_id)
    await session.commit()

async def process_message(message_id):
  async with session_factory() as session:
    outbox_repository = OutboxDAO(session=session)
    await outbox_repository.mark_as_processed(message_id)
    await session.commit()

def deserialize_event(payload, event_class):
  event_dict = json.loads(payload)
  event_dict.pop('event_type')
  event = event_class(**event_dict)
  return event

async def do_task(message_id, handler_class, event_class):
  print(f'Task: {message_id}')
  try:
    async with session_factory() as session:
      outbox_repository = OutboxDAO(session=session)
      message = await outbox_repository.get_by_id(message_id)
      event = deserialize_event(payload=message.payload, event_class=event_class)
      uow = SqlAlchemyUnitOfWork(session)
      handler = handler_class(uow)
      await handler.handle(event)
  except Exception as e:
    await handle_errors(message_id=message_id, e=e)
    return
  await process_message(message_id)


async def main():
  args = get_args()
  print(f'Listen to events: {args.event_type}')

  handler_class = handler_by_event_type.get(args.event_type)
  event_class = event_by_type.get(args.event_type)
  if handler_class is None:
    raise ValueError('Wrong event_type name')

  while True:
    async with session_factory() as session:
      outbox_repository = OutboxDAO(session=session)
      unprocessed_message_ids = await outbox_repository.get_unprocessed_message_ids(event_type=args.event_type, limit=50)
      print(unprocessed_message_ids)
    if not unprocessed_message_ids:
      await asyncio.sleep(1)

    tasks = [do_task(message_id, handler_class, event_class) for message_id in unprocessed_message_ids]

    await asyncio.gather(*tasks)


if __name__ == '__main__':
  asyncio.run(main())