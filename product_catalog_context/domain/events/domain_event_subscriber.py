from abc import ABC, abstractmethod


class DomainEventSubscriber(ABC):
  @abstractmethod
  def handle(self, event):
    pass
