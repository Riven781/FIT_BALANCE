from abc import ABC, abstractmethod

from identity_and_access_context.application.unit_of_work.unit_of_work import UnitOfWork


class UnitOfWorkFactory(ABC):
  @abstractmethod
  def create_persistent(self) -> UnitOfWork:
    pass

  @abstractmethod
  def create_ephemeral(self) -> UnitOfWork:
    pass