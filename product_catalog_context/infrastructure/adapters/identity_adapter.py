from identity_and_access_context.public.api.identity_api import IdentityApi


class IdentityAdapter:
  def __init__(self, identity_api: IdentityApi):
    self.identity_api = identity_api
    
  async def get_current_user_id(self, credentials):
    authenticated_user = await self.identity_api.get_current_user(credentials)
    return authenticated_user.user_id