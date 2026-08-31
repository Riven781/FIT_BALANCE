from redis.asyncio import Redis

from identity_and_access_context.domain.session.session_repository import SessionRepository
from identity_and_access_context.application.unit_of_work.unit_of_work import UnitOfWork
from identity_and_access_context.infrastructure.redis_repository.session_repository import RedisSessionRepository


class RedisUnitOfWork(UnitOfWork):
  def __init__(self, redis_client: Redis):
    self.redis_client = redis_client
    self._session = None

  async def __aenter__(self):
    return self
  
  async def __aexit__(self, exc_type, exc, tb):
    pass

  @property
  def sessions(self) -> SessionRepository:
    if self._session is None:
      self._session = RedisSessionRepository(self.redis_client)
      return self._session
    return self._session
