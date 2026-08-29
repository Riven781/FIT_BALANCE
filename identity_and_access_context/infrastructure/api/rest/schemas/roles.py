from pydantic import BaseModel
from identity_and_access_context.domain.role import Role


class SetRolesRequest(BaseModel):
  roles: list[Role]