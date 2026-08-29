from abc import ABC, abstractmethod

from product_catalog_context.domain.users import User


class AuthenticationProvider(ABC):

  @abstractmethod
  async def login(self, user: User):
    pass

  @abstractmethod
  async def logout(self, credential_value):
    pass

  @abstractmethod
  async def authenticate(self, credential_value):
    pass

  @abstractmethod
  async def refresh(self, credential_value):
    pass