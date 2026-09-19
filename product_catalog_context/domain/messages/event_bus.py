from product_catalog_context.domain.messages.message import DomainEvent
from product_catalog_context.domain.messages.message_bus import MessageBus


class EventBus(MessageBus):
  def __init__(self):
    self.subscribers = {}

  def subscribe(self, event_class, handler):
    self.subscribers.setdefault(event_class, []).append(handler)
    
  async def publish(self, event: DomainEvent):
    handlers = self.subscribers.get(type(event), [])
    for handler in handlers:
      await handler.handle(event)