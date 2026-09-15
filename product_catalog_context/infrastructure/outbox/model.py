from dataclasses import dataclass
from datetime import datetime, timezone


class OutboxMessage:
  message_id: int
  event_type: str
  payload: str
  occurred_at: datetime
  processed_at: datetime | None
  attempts : int

  def __init__(self, message_id, event_type, payload,  occurred_at, processed_at, attempts):
    self.message_id = message_id
    self.event_type = event_type
    self.payload = payload
    self.occurred_at = occurred_at
    self.processed_at = processed_at
    self.attempts = attempts

  def process(self):
    self.processed_at = datetime.now(timezone.utc)
