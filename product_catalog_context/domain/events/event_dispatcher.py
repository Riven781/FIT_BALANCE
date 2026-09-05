from abc import ABC, abstractmethod
from product_catalog_context.domain.events.event import DomainEvent


class AbstractEventDispatcher(ABC):

  @abstractmethod
  def register(self, event_type, handler):
    pass

  @abstractmethod
  async def dispatch(self, events: list[DomainEvent]):
    pass