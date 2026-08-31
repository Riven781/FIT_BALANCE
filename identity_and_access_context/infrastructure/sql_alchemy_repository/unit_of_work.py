from identity_and_access_context.domain.refresh_token.refresh_token_repository import RefreshTokenRepository
from identity_and_access_context.application.unit_of_work.unit_of_work import UnitOfWork
from sqlalchemy.ext.asyncio import AsyncSession
from identity_and_access_context.domain.user.user_repository import UserRepository
from identity_and_access_context.domain.user_roles.user_roles_repository import UserRolesRepository
from identity_and_access_context.infrastructure.sql_alchemy_repository.refresh_token_repository import SqlAlchemyRefreshTokenRepository
from identity_and_access_context.infrastructure.sql_alchemy_repository.user_repository import SqlAlchemyUserRepository
from identity_and_access_context.infrastructure.sql_alchemy_repository.user_roles_repository import SqlAlchemyUserRolesRepository


class SqlAlchemyUnitOfWork(UnitOfWork):
  def __init__(self, session: AsyncSession):
    self.session = session
    self._users = None
    self._user_roles = None
    self._refresh_token = None

  async def __aenter__(self):
    return self

  async def __aexit__(self, exc_type, exc, tb):
    if exc is not None:
      await self.rollback()
    else:
      await self.commit()

  async def commit(self) -> None:
    await self.session.commit()

  async def rollback(self) -> None:
    await self.session.rollback()

  @property
  def users(self) -> UserRepository:
    if self._users is None:
      self._users = SqlAlchemyUserRepository(self.session)
      return self._users
    return self._users

  @property
  def user_roles(self) -> UserRolesRepository:
    if self._user_roles is None:
      self._user_roles = SqlAlchemyUserRolesRepository(self.session)
      return self._user_roles
    return self._user_roles

  @property
  def refresh_tokens(self) -> RefreshTokenRepository:
    if self._refresh_token is None:
      self._refresh_token = SqlAlchemyRefreshTokenRepository(self.session)
      return self._refresh_token
    return self._refresh_token
