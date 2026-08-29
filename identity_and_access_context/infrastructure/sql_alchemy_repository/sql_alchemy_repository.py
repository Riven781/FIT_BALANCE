from abc import ABC, abstractmethod
from sqlalchemy import insert, inspect, select
from sqlalchemy.ext.asyncio import AsyncSession

class BaseSqlAlchemyRepository(ABC):
  def __init__(self, session: AsyncSession):
    self.session = session

  async def _save(self, obj):
    state = inspect(obj)
    is_new = state.transient
    self.session.add(obj)
    if is_new:
      await self.session.flush()
