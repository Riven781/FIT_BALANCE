from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.event import listens_for
from config import DB_PATH

sqlite_engine = create_async_engine(f'sqlite+aiosqlite:///{DB_PATH}')

session_factory = async_sessionmaker(sqlite_engine, class_=AsyncSession, expire_on_commit=False)

def get_sqlalchemy_session_factory():
  return session_factory

async def get_session():
  async with session_factory() as session:
    yield session

@listens_for(sqlite_engine.sync_engine, 'connect')
def set_sqlite_pragma(dbapi_connection, connection_record):
  cursor = dbapi_connection.cursor()
  cursor.execute('PRAGMA foreign_keys=ON')
  cursor.close()