from identity_and_access_context.application.command.login import LoginCommand
from identity_and_access_context.application.errors import   AuthenticationRequired, EmailAlreadyExists, InvalidCredentialsError, PasswordsMustBeTheSame, UsernameAlreadyExists
from identity_and_access_context.domain.auth_credentials.jwt_credential import JwtAccessTokenCredential, JwtRefreshTokenCredential
from identity_and_access_context.domain.auth_credentials.session_credential import SessionCredential
from identity_and_access_context.domain.auth_method import AuthMethod
from identity_and_access_context.application.authentication_provider_factory import AuthenticationProviderFactory
from identity_and_access_context.domain.authentication_provider.errors import CredentialNotFound, InvalidCredential
from identity_and_access_context.domain.user.user_repository import UserRepository
from identity_and_access_context.domain.session.session import Session
from identity_and_access_context.domain.user.user import User
from identity_and_access_context.infrastructure.security import hash_value


class AuthenticationService:
  def __init__(self, authentication_provider_factory: AuthenticationProviderFactory, user_repository : UserRepository, user_roles_cache=None):
    self.user_repository = user_repository
    self.authentication_provider_factory = authentication_provider_factory
    self.user_roles_cache = user_roles_cache

  async def login(self, login_command: LoginCommand):
    hashed_password = hash_value(login_command.password)
    user = await self.user_repository.get_from_authentic_credentials(login_command.username, hashed_password)
    if user is None:
      raise InvalidCredentialsError()
    #await self.user_roles_cache.set(user.user_id, user.roles)
    provider = self.authentication_provider_factory.create_by_auth_method(login_command.auth_method)
    return await provider.login(user)

  async def logout(self, credential: SessionCredential | JwtAccessTokenCredential):
    provider = self.authentication_provider_factory.create_by_credential(credential)
    try:
      await provider.logout(credential.value)
    except CredentialNotFound as e:
      raise InvalidCredentialsError() from e

  async def authenticate(self, credential: SessionCredential | JwtAccessTokenCredential) -> int:
    provider = self.authentication_provider_factory.create_by_credential(credential)
    try:
      user_id = await provider.authenticate(credential.value)
    except (InvalidCredential, CredentialNotFound) as e:
      raise InvalidCredentialsError() from e
    return user_id
  
  async def refresh(self, credential: SessionCredential | JwtRefreshTokenCredential):
    provider = self.authentication_provider_factory.create_by_credential(credential)
    try:
      refreshed_credential =  await provider.refresh(credential.value)
    except (InvalidCredential, CredentialNotFound) as e:
      raise InvalidCredentialsError() from e
    return refreshed_credential
