from sqlalchemy import insert, update

from identity_and_access_context.domain.repository.errors import ConcurrentModification
from identity_and_access_context.domain.user_roles.user_roles_repository import UserRolesRepository
from identity_and_access_context.domain.user_roles.user_roles import UserRoles
from identity_and_access_context.infrastructure.sql_alchemy_repository.mapper import user_roles_table
from identity_and_access_context.infrastructure.sql_alchemy_repository.sql_alchemy_repository import BaseSqlAlchemyRepository


class SqlAlchemyUserRolesRepository(UserRolesRepository, BaseSqlAlchemyRepository):
  def __init__(self, session):
    super().__init__(session)

  async def  get_by_user_id(self, user_roles_id):
    return await self.session.get(UserRoles, user_roles_id)

  async def save(self, user_roles: UserRoles):
    if user_roles.version is None:
      self.session.add(user_roles)
      user_roles.version = 1
    else:
      stmt = (
        update(user_roles_table)
        .where(
          user_roles_table.c.version == user_roles.version, 
          user_roles_table.c.user_id == user_roles.user_id
        )
        .values(
          version = user_roles_table.c.version + 1
        )
        .returning(user_roles_table.c.version))
      new_version = await self.session.scalar(stmt)

      if new_version is None:
        raise  ConcurrentModification()
      
      user_roles.version = new_version

  async def delete(self, user_roles):
    await self.session.delete(user_roles)

 