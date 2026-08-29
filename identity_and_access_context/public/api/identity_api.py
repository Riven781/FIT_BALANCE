from redis import AuthenticationError

from identity_and_access_context.application.authentication_service import AuthenticationService
from identity_and_access_context.application.errors import AmbiguousAuthentication, InvalidCredentialsError, AuthenticationRequired, ServiceError
from identity_and_access_context.domain.auth_credentials.jwt_credential import JwtCredential
from identity_and_access_context.domain.auth_credentials.session_credential import SessionCredential
from identity_and_access_context.application.to_authentication_credential import to_authentication_credential
from identity_and_access_context.public.contracts import AuthenticatedUser
from shared.infrastructure.fastapi.security.contracts import RawAuthenticationCredentials


class IdentityApi:
  def __init__(self, authentication_service: AuthenticationService):
    self.authentication_service = authentication_service

  async def get_current_user(self, credentials: RawAuthenticationCredentials) -> int:
    try:
      credential = to_authentication_credential(raw=credentials)
      user_id = await self.authentication_service.authenticate(credential)
    except (AmbiguousAuthentication, AuthenticationRequired, InvalidCredentialsError) as e:
      raise AuthenticationError() from e
  
    return AuthenticatedUser(user_id)
