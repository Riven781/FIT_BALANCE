from dataclasses import dataclass

from identity_and_access_context.domain.auth_method import AuthMethod


@dataclass
class LoginCommand:
  auth_method: AuthMethod
  username: str
  password: str