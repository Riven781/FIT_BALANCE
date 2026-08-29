from identity_and_access_context.application.access_service import AccessService
from identity_and_access_context.application.errors import InsufficientPermissions
from identity_and_access_context.public.contracts import AuthorizedUser


class AccessApi:
  def __init__(self, access_service: AccessService):
    self._access_service = access_service

  async def get_authorized_user(self, user_id, role): #maybe return AuthorizedUser or raise exception
    try:
      await self._access_service.authorize(user_id, role)
    except InsufficientPermissions:
      return None
    return AuthorizedUser(user_id=user_id, role=role)

