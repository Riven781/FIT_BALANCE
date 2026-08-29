from identity_and_access_context.application.errors import AmbiguousAuthentication, AuthenticationRequired
from shared.infrastructure.fastapi.security.contracts import RawAuthenticationCredentials
from identity_and_access_context.application.authentication_service import AuthenticationService
from identity_and_access_context.domain.auth_credentials.jwt_credential import JwtAccessTokenCredential, JwtCredential
from identity_and_access_context.domain.auth_credentials.session_credential import SessionCredential


def to_authentication_credential(raw: RawAuthenticationCredentials):
  if raw.session_id is not None and raw.token is not None:
    raise AmbiguousAuthentication()
  if raw.session_id is not None:
    return SessionCredential(raw.session_id)
  if raw.token is not None:
    return JwtAccessTokenCredential(raw.token)
  raise AuthenticationRequired()