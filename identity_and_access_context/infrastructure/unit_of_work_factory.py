from identity_and_access_context.application.unit_of_work.unit_of_work import UnitOfWork
from identity_and_access_context.application.unit_of_work.unit_of_work_factory import UnitOfWorkFactory
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from identity_and_access_context.infrastructure.redis_repository.unit_of_work import RedisUnitOfWork
from identity_and_access_context.infrastructure.sql_alchemy_repository.unit_of_work import SqlAlchemyUnitOfWork


class DefaultUnitOfWorkFactory(UnitOfWorkFactory):
  def __init__(self, session: AsyncSession, redis_client: Redis):
    self.session = session
    self.redis_client = redis_client

  def create_persistent(self) -> UnitOfWork:
    return SqlAlchemyUnitOfWork(self.session)

  def create_ephemeral(self) -> UnitOfWork:
    return RedisUnitOfWork(self.redis_client)