from abc import ABC, abstractmethod
from product_catalog_context.domain.events.domain_event_subscriber import DomainEventSubscriber
from product_catalog_context.domain.events.event import DomainEvent



class DomainEventPublisher():
  def __init__(self):
    self.subscribers : dict[type, list[DomainEventSubscriber]] = {}
    self.global_subscribers : list[DomainEventSubscriber] = []

  def subscribe(self, event_type,  subscriber: DomainEventSubscriber):
    if self.subscribers.get(event_type) is None:
      self.subscribers[event_type] = []
    self.subscribers[event_type].append(subscriber)

  def global_subscribe(self, subscriber: DomainEventSubscriber):
    self.global_subscribers.append(subscriber)

  async def publish(self, events: list[DomainEvent]):
    for event in events:
      for global_subscriber in self.global_subscribers:
        await global_subscriber.handle(event)
      subscribers_to_event = self.subscribers.get(type(event), [])
      for subscriber in subscribers_to_event:
        await subscriber.handle(event)
