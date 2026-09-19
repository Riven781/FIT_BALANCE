from abc import ABC, abstractmethod


class DomainMessageSubscriber(ABC):
  @abstractmethod
  async def handle(self, message):
    pass
