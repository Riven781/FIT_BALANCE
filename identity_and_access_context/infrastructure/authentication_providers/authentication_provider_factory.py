from identity_and_access_context.domain.auth_credentials.jwt_credential import JwtCredential
from identity_and_access_context.domain.auth_credentials.session_credential import SessionCredential
from identity_and_access_context.domain.auth_method import AuthMethod
from identity_and_access_context.infrastructure.authentication_providers.jwt_authentication_provider import JwtAuthenticationProvider
from identity_and_access_context.infrastructure.authentication_providers.session_authentication_provider import SessionAuthenticationProvider


class DefaultAuthenticationProviderFactory:
  def __init__(self, session_repository, refresh_token_repository):
    self.session_repository = session_repository
    self.refresh_token_repository = refresh_token_repository

  def create_by_auth_method(self, auth_method: AuthMethod):
    if auth_method == AuthMethod.JWT:
      return JwtAuthenticationProvider(refresh_token_repository=self.refresh_token_repository)
    if auth_method == AuthMethod.SESSION:
      return SessionAuthenticationProvider(session_repository=self.session_repository)
    raise ValueError(f"UnsupportedAuthMethod: {auth_method}")

  def create_by_credential(self, credential: SessionCredential | JwtCredential):
    if isinstance(credential, JwtCredential):
      return JwtAuthenticationProvider(refresh_token_repository=self.refresh_token_repository)
    if isinstance(credential, SessionCredential):
      return SessionAuthenticationProvider(session_repository=self.session_repository)
    raise ValueError("UnsupportedCredentialType")