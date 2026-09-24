from sqlalchemy import Column, DateTime, Double, ForeignKey, Integer, PrimaryKeyConstraint, String, Table, insert, join, text
from sqlalchemy.orm import registry

from product_catalog_context.infrastructure.outbox.model import OutboxMessage

outbox_mapper_registry = registry()


outbox_message_table = Table(
  "OutboxMessage",
  outbox_mapper_registry.metadata,
  Column("id", Integer, primary_key=True, nullable=False),
  Column("message_type", String, nullable=False),
  Column("message_name", String, nullable=False),
  Column("payload", String, nullable=False),
  Column("occurred_at", DateTime, server_default=text("CURRENT_TIMESTAMP")),
  Column("processed_at", DateTime),
  Column('retry_count', Integer, default=0)
)


outbox_mapper_registry.map_imperatively(OutboxMessage, outbox_message_table, properties={
  "message_id": outbox_message_table.c.id
})