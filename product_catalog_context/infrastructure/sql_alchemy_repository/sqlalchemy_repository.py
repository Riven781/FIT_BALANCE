from abc import ABC, abstractmethod
from sqlalchemy import insert, inspect, select
import sqlalchemy
import sqlalchemy.exc
from sqlalchemy.ext.asyncio import AsyncSession

from product_catalog_context.infrastructure.aiosqlite_repository.errors_mapper import mapped_error

class BaseSqlAlchemyRepository(ABC):
  def __init__(self, session: AsyncSession):
    self.session = session

  async def _save(self, obj):
    state = inspect(obj)
    is_new = state.transient
    self.session.add(obj)
    if is_new:
      try:
        await self.session.flush()
      except sqlalchemy.exc.SQLAlchemyError as e:
        raise mapped_error(e) from e

  async def _execute(self, query, params=None):
    try:
      result = await self.session.execute(query, params)
    except sqlalchemy.exc.SQLAlchemyError as e:
      raise mapped_error(e) from e
    return result
  