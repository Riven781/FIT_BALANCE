from dataclasses import asdict
from datetime import datetime, timezone
import json
from sqlalchemy import insert
from product_catalog_context.domain.events.domain_event_subscriber import DomainEventSubscriber
from sqlalchemy.ext.asyncio import AsyncSession
from product_catalog_context.domain.events.event import DomainEvent
from product_catalog_context.infrastructure.outbox.model import OutboxMessage
from product_catalog_context.infrastructure.outbox.repository import OutboxDAO





class OutboxSubscriber(DomainEventSubscriber):
  def __init__(self, outbox_repository: OutboxDAO):
    self.outbox_repository = outbox_repository

  async def handle(self, event: DomainEvent):
    outbox = OutboxMessage(event_type=event.event_type, payload=json.dumps(asdict(event)), occurred_at=datetime.now(timezone.utc))
    await self.outbox_repository.insert(outbox)
  