from abc import ABC, abstractmethod
from identity_and_access_context.domain.auth_credentials.jwt_credential import JwtCredential
from identity_and_access_context.domain.auth_credentials.session_credential import SessionCredential
from identity_and_access_context.domain.auth_method import AuthMethod
from identity_and_access_context.domain.authentication_provider.authentication_provider import AuthenticationProvider

class AuthenticationProviderFactory(ABC):

  @abstractmethod
  def create_by_auth_method(self, auth_method: AuthMethod) -> AuthenticationProvider:
    pass

  @abstractmethod
  def create_by_credential(self, credential: SessionCredential | JwtCredential) -> AuthenticationProvider:
    pass