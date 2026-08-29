from httpx import delete
from sqlalchemy import insert, inspect, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.sqlite import insert
from identity_and_access_context.domain.user.user_repository import UserRepository
from identity_and_access_context.domain.role import Role
from identity_and_access_context.domain.user.user import User
from identity_and_access_context.infrastructure.sql_alchemy_repository.mapper import UserRoleModel
from identity_and_access_context.infrastructure.sql_alchemy_repository.sql_alchemy_repository import BaseSqlAlchemyRepository

class SqlAlchemyUserRepository(UserRepository, BaseSqlAlchemyRepository):
  def __init__(self, session):
    super().__init__(session)

  async def exists_by_email(self, email):
    stmt = select(select(User.user_id)
      .where(User.email == email)
      .exists())
    result = await self.session.scalar(stmt)
    return result

  async def exists_by_username(self, username):
    stmt = select(select(User.user_id)
      .where(User.username == username)
      .exists())
    result = await self.session.scalar(stmt)
    return result


  async def get_by_id(self, user_id):
    return await self.session.get(User, user_id)

  async def get_from_authentic_credentials(self, username, hashed_password):
    stmt = (select(User)
      .where(User.username == username)
      .where(User.hashed_password == hashed_password))
    result = await self.session.execute(stmt)
    return result.scalar_one_or_none()


  async def delete(self, user):
    await self.session.delete(user)

  async def save(self, user: User):
    await self._save(user)

