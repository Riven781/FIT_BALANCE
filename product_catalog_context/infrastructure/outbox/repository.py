from sqlalchemy import select, update

from datetime import datetime, timezone

from product_catalog_context.infrastructure.outbox.model import OutboxMessage
from product_catalog_context.infrastructure.sql_alchemy_repository.sqlalchemy_repository import BaseSqlAlchemyRepository
from product_catalog_context.infrastructure.outbox.mapper import outbox_message_table

class OutboxDAO():
  def __init__(self, session):
    self.session = session

  async def get_unprocessed_message_ids(self, event_type, limit):
    query = select(
      OutboxMessage.message_id
    ).where(
      OutboxMessage.event_type == event_type, 
      OutboxMessage.processed_at.is_(None),
      OutboxMessage.attempts < 5
    ).order_by(
      OutboxMessage.occurred_at.asc()
    ).limit(
      limit=limit
    )
    result = await self.session.scalars(query)
    return result.all()

  async def get_by_id(self, message_id) -> OutboxMessage:
    return await self.session.get(OutboxMessage, message_id)


  async def increase_attempt(self, message_id):
    query = update(
      OutboxMessage
    ).where(
      OutboxMessage.message_id == message_id
    ).values(
      attempts=OutboxMessage.attempts + 1
    )
    await self.session.execute(query)

  async def mark_as_processed(self, message_id):
    query = update(
      OutboxMessage
    ).where(
      OutboxMessage.message_id == message_id
    ).values(
      processed_at=datetime.now(timezone.utc)
    )
    await self.session.execute(query)
