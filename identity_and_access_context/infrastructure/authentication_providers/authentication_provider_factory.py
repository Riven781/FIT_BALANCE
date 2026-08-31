from identity_and_access_context.application.authentication_provider_factory import AuthenticationProviderFactory
from identity_and_access_context.application.unit_of_work.unit_of_work import UnitOfWork
from identity_and_access_context.domain.auth_credentials.jwt_credential import JwtCredential
from identity_and_access_context.domain.auth_credentials.session_credential import SessionCredential
from identity_and_access_context.domain.auth_method import AuthMethod
from identity_and_access_context.infrastructure.authentication_providers.jwt_authentication_provider import JwtAuthenticationProvider
from identity_and_access_context.infrastructure.authentication_providers.session_authentication_provider import SessionAuthenticationProvider


class DefaultAuthenticationProviderFactory(AuthenticationProviderFactory):
  def __init__(self, unit_of_work_factory: UnitOfWork):
    self.unit_of_work_factory = unit_of_work_factory

  def create_by_auth_method(self, auth_method: AuthMethod):
    if auth_method == AuthMethod.JWT:
      unit_of_work = self.unit_of_work_factory.create_persistent()
      return JwtAuthenticationProvider(unit_of_work=unit_of_work)
    if auth_method == AuthMethod.SESSION:
      unit_of_work = self.unit_of_work_factory.create_ephemeral()
      return SessionAuthenticationProvider(unit_of_work=unit_of_work)
    raise ValueError(f"UnsupportedAuthMethod: {auth_method}")

  def create_by_credential(self, credential: SessionCredential | JwtCredential):
    if isinstance(credential, JwtCredential):
      unit_of_work = self.unit_of_work_factory.create_persistent()
      return JwtAuthenticationProvider(unit_of_work=unit_of_work)
    if isinstance(credential, SessionCredential):
      unit_of_work = self.unit_of_work_factory.create_ephemeral()
      return SessionAuthenticationProvider(unit_of_work=unit_of_work)
    raise ValueError("UnsupportedCredentialType")