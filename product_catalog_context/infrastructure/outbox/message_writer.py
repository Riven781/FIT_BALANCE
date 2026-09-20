from dataclasses import asdict
import json
from datetime import datetime, timezone
from product_catalog_context.application.ports.message_writer import MessageWriter
from product_catalog_context.domain.messages.message import DomainCommand, DomainEvent
from product_catalog_context.infrastructure.outbox.model import OutboxMessage


class SqlAlchemyOutboxMessageWriter(MessageWriter):
  def __init__(self, session):
    self.session = session

  async def write(self, message):
    print(
        "WRITE",
        message,
        "writer:",
        id(self),
        "session:",
        id(self.session),
    )
    if isinstance(message, DomainEvent):
      outbox = OutboxMessage(message_type='event', message_name=message.event_type, payload=json.dumps(asdict(message)), occurred_at=datetime.now(timezone.utc))
    elif isinstance(message, DomainCommand):
      outbox = OutboxMessage(message_type='command', message_name=message.command_type, payload=json.dumps(asdict(message)), occurred_at=datetime.now(timezone.utc))
    else:
      return ValueError('Only events and commands are handled')
    self.session.add(outbox)