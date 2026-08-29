from abc import ABC, abstractmethod

from identity_and_access_context.domain.user_roles.user_roles import UserRoles

class UserRolesRepository(ABC):

  @abstractmethod
  async def get_by_user_id(self, user_roles_id: int) -> UserRoles:
    pass

  @abstractmethod
  async def save(self, user_roles: UserRoles):
    pass

  @abstractmethod
  async def delete(self, user_roles: UserRoles):
    pass