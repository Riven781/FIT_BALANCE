from identity_and_access_context.application.errors import InsufficientPermissions


class AccessService:
  def __init__(self, user_roles_repository):
    self.user_roles_repository = user_roles_repository

  async def authorize(self, user_id, required_role):
    user_roles = await self.user_roles_repository.get_by_user_id(user_id)
    if user_roles is None or not user_roles.has_role(required_role):
      raise InsufficientPermissions()
    