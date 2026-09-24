from dataclasses import asdict
from datetime import datetime, timezone
import json
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession
from product_catalog_context.application.unit_of_work import UnitOfWorkContext
from product_catalog_context.domain.messages.domain_message_subscriber import DomainMessageSubscriber
from product_catalog_context.domain.messages.message import DomainCommand, DomainEvent, DomainMessage
from product_catalog_context.infrastructure.outbox.model import OutboxMessage
from product_catalog_context.infrastructure.outbox.repository import OutboxDAO





class OutboxSubscriber(DomainMessageSubscriber):
  async def handle(self, message, uow_context: UnitOfWorkContext):
    await uow_context.message_writer.write(message)
    


class DoubleOutboxSubscriber(DomainMessageSubscriber):
  async def handle(self, message, uow_context: UnitOfWorkContext):
    await uow_context.message_writer.write(message)
    await uow_context.message_writer.write(message)