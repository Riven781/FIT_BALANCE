from abc import ABC, abstractmethod
from product_catalog_context.domain.messages.domain_message_subscriber import DomainMessageSubscriber
from product_catalog_context.domain.messages.message import DomainMessage



class DomainMessagePublisher():
  def __init__(self):
    self.subscribers : dict[type, list[DomainMessageSubscriber]] = {}
    self.global_subscribers : list[DomainMessageSubscriber] = []

  def subscribe(self, message_type,  subscriber: DomainMessageSubscriber):
    if self.subscribers.get(message_type) is None:
      self.subscribers[message_type] = []
    self.subscribers[message_type].append(subscriber)

  def global_subscribe(self, subscriber: DomainMessageSubscriber):
    self.global_subscribers.append(subscriber)

  async def publish(self, messages: list[DomainMessage]):
    for message in messages:
      for global_subscriber in self.global_subscribers:
        await global_subscriber.handle(message)
      subscribers_to_event = self.subscribers.get(type(message), [])
      for subscriber in subscribers_to_event:
        await subscriber.handle(message)
