from abc import ABC, abstractmethod
from identity_and_access_context.domain.refresh_token.refresh_token_repository import RefreshTokenRepository
from identity_and_access_context.domain.session.session_repository import SessionRepository
from identity_and_access_context.domain.user.user_repository import UserRepository
from identity_and_access_context.domain.user_roles.user_roles_repository import UserRolesRepository

class UnitOfWork(ABC):

  @abstractmethod
  async def __aenter__(self):
    pass

  @abstractmethod
  async def __aexit__(self, exc_type, exc, tb):
    pass

  async def commit(self) -> None:
    pass

  async def rollback(self) -> None:
    pass

  @property
  def users(self) -> UserRepository:
    pass

  @property
  def user_roles(self) -> UserRolesRepository:
    pass

  @property
  def refresh_tokens(self) -> RefreshTokenRepository:
    pass

  @property
  def sessions(self) -> SessionRepository:
    pass

