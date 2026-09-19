from dataclasses import asdict
from datetime import datetime, timezone
import json
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession
from product_catalog_context.domain.messages.domain_message_subscriber import DomainMessageSubscriber
from product_catalog_context.domain.messages.message import DomainCommand, DomainEvent, DomainMessage
from product_catalog_context.infrastructure.outbox.model import OutboxMessage
from product_catalog_context.infrastructure.outbox.repository import OutboxDAO





class OutboxSubscriber(DomainMessageSubscriber):
  def __init__(self, outbox_repository: OutboxDAO):
    self.outbox_repository = outbox_repository

  async def handle(self, message):
    if isinstance(message, DomainEvent):
      outbox = OutboxMessage(message_type='event', message_name=message.event_type, payload=json.dumps(asdict(message)), occurred_at=datetime.now(timezone.utc))
    elif isinstance(message, DomainCommand):
      outbox = OutboxMessage(message_type='command', message_name=message.command_type, payload=json.dumps(asdict(message)), occurred_at=datetime.now(timezone.utc))
    else:
      return ValueError('Only events and commands are handled')
    await self.outbox_repository.insert(outbox)
  