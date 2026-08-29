from dataclasses import dataclass
from identity_and_access_context.domain.role import Role

@dataclass
class AuthenticatedUser:
  user_id: int | None


@dataclass
class AuthorizedUser:
  user_id: int
  role: Role