from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from pathlib import Path
from sqlalchemy.pool import StaticPool

def get_session_factory(db_path):

  engine = create_async_engine(f'sqlite+aiosqlite:///{db_path}', poolclass=StaticPool)
  session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
  return session_factory
