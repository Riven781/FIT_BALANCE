from abc import ABC, abstractmethod

from identity_and_access_context.domain.session.session import Session

class SessionRepository(ABC):

  @abstractmethod
  async def save(self, session: Session):
    pass

  @abstractmethod
  async def get_by_id(self, session_id: str) -> Session:
    pass

  @abstractmethod
  async def get_all_by_user_id(self, user_id: str) -> list[Session]:
    pass

  @abstractmethod
  async def get_all_by_session_id(self, session_id: str) -> list[Session]:
    pass

  @abstractmethod
  async def delete_by_id(self, session_id: str):
    pass

  @abstractmethod
  async def next_id(self) -> str:
    pass