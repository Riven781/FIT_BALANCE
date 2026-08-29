from abc import ABC, abstractmethod

from product_catalog_context.domain.users import User

class UserRepository(ABC):

  @abstractmethod
  async def get_by_id(self, user_id: int) -> User:
    pass

  @abstractmethod
  async def get_from_authentic_credentials(self, username: str, hashed_password: str) -> User:
    pass

  @abstractmethod
  async def exists_by_username(self, username: str):
    pass

  @abstractmethod
  async def exists_by_email(self, email: str):
    pass

  @abstractmethod
  async def delete(self, user: User):
    pass

  @abstractmethod
  async def save(self, user: User):
    pass
