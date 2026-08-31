from identity_and_access_context.application.access_service import AccessService
from identity_and_access_context.application.errors import UserNotFoundError, UserRolesChangedSinceRead
from identity_and_access_context.application.unit_of_work.unit_of_work import UnitOfWork
from identity_and_access_context.domain.repository.errors import ConcurrentModification
from identity_and_access_context.domain.user_roles.user_roles_repository import UserRolesRepository
from identity_and_access_context.domain.role import Role


class UserRolesManagementService:
  def __init__(self, unit_of_work : UnitOfWork, access_service: AccessService):
    self.access_service = access_service
    self.unit_of_work = unit_of_work

  async def set_roles(self, admin_id, user_id, roles):
    async with self.unit_of_work:
      await self.access_service.authorize(admin_id, Role.ADMIN)
      user_roles = await self.unit_of_work.user_roles.get_by_user_id(user_id)
      if user_roles is None:
        raise UserNotFoundError()
      user_roles.set_roles(roles)
      try:
        await self.unit_of_work.user_roles.save(user_roles)
      except ConcurrentModification as e:
        raise UserRolesChangedSinceRead() from e


