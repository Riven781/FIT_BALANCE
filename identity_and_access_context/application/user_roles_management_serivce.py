from identity_and_access_context.application.access_service import AccessService
from identity_and_access_context.application.errors import UserNotFoundError, UserRolesChangedSinceRead
from identity_and_access_context.domain.repository.errors import ConcurrentModification
from identity_and_access_context.domain.user_roles.user_roles_repository import UserRolesRepository
from identity_and_access_context.domain.role import Role


class UserRolesManagementService:
  def __init__(self, user_roles_repository: UserRolesRepository, access_service: AccessService):
    self.access_service = access_service
    self.user_roles_repository = user_roles_repository

  async def set_roles(self, admin_id, user_id, roles):
    await self.access_service.authorize(admin_id, Role.ADMIN)
    user_roles = await self.user_roles_repository.get_by_user_id(user_id)
    if user_roles is None:
      raise UserNotFoundError()
    user_roles.set_roles(roles)
    try:
      await self.user_roles_repository.save(user_roles)
    except ConcurrentModification as e:
      raise UserRolesChangedSinceRead() from e


