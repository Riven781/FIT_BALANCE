from abc import ABC, abstractmethod

from product_catalog_context.domain.messages.message import DomainMessage


class MessageWriter(ABC):
  @abstractmethod
  async def write(self, message: DomainMessage) -> None:
    pass
