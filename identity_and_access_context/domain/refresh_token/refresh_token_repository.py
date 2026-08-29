from abc import ABC, abstractmethod

from identity_and_access_context.domain.refresh_token.refresh_token import RefreshToken

class RefreshTokenRepository(ABC):

  @abstractmethod
  async def get_by_id(self, token_id) -> RefreshToken:
    pass

  @abstractmethod
  async def get_by_hash(self, token_hash) -> RefreshToken:
    pass

  @abstractmethod
  async def delete(self, token: RefreshToken):
    pass

  @abstractmethod
  async def save(self, token: RefreshToken):
    pass
