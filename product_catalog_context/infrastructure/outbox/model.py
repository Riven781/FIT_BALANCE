from dataclasses import dataclass
from datetime import datetime, timezone


class OutboxMessage:
  message_id: int
  message_type: str #event or command
  message_name: str
  payload: str
  occurred_at: datetime
  processed_at: datetime | None
  retry_count : int

  def __init__(self, message_type, message_name, payload,  occurred_at, processed_at = None, retry_count = 0, message_id = None):
    self.message_id = message_id
    self.message_type = message_type
    self.message_name = message_name
    self.payload = payload
    self.occurred_at = occurred_at
    self.processed_at = processed_at
    self.retry_count = retry_count

  def process(self):
    self.processed_at = datetime.now(timezone.utc)
