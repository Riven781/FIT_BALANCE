from datetime import datetime
from identity_and_access_context.application.authentication_service import AuthenticationService
import pytest
import pytest_asyncio
from config import REDIS_HOST, REDIS_PORT
from identity_and_access_context.application.access_service import AccessService
from identity_and_access_context.domain.user_roles.user_roles import UserRoles
from identity_and_access_context.domain.refresh_token.refresh_token import RefreshToken
from identity_and_access_context.domain.role import Role
from identity_and_access_context.domain.user.user import User
from identity_and_access_context.infrastructure.authentication_providers.authentication_provider_factory import DefaultAuthenticationProviderFactory
from identity_and_access_context.infrastructure.authentication_providers.jwt_authentication_provider import JwtAuthenticationProvider
from identity_and_access_context.infrastructure.redis_repository.session_repository import RedisSessionRepository
from identity_and_access_context.infrastructure.redis_repository.user_roles_cache import RedisUserRolesCache
from identity_and_access_context.infrastructure.security import hash_value
from identity_and_access_context.infrastructure.authentication_providers.session_authentication_provider import SessionAuthenticationProvider
from identity_and_access_context.infrastructure.sql_alchemy_repository.refresh_token_repository import SqlAlchemyRefreshTokenRepository
from identity_and_access_context.infrastructure.sql_alchemy_repository.user_repository import SqlAlchemyUserRepository
from identity_and_access_context.infrastructure.sql_alchemy_repository.user_roles_repository import SqlAlchemyUserRolesRepository
from shared.database.session import SessionLocal
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from identity_and_access_context.infrastructure.sql_alchemy_repository.mapper import mapper_registry
from sqlalchemy.event import listens_for
import redis.asyncio as redis
from identity_and_access_context.domain.session.session import Session, SessionData
import json
from identity_and_access_context.infrastructure.unit_of_work_factory import DefaultUnitOfWorkFactory
from identity_and_access_context.infrastructure.sql_alchemy_repository.unit_of_work import SqlAlchemyUnitOfWork
from identity_and_access_context.infrastructure.redis_repository.unit_of_work import RedisUnitOfWork

@pytest_asyncio.fixture
async def db_session():
  engine = create_async_engine(f'sqlite+aiosqlite:///:memory:')
  SessionTest = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
  @listens_for(engine.sync_engine, 'connect')
  def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute('PRAGMA foreign_keys=ON')
    cursor.close()
  async with engine.begin() as conn:
    await conn.run_sync(mapper_registry.metadata.create_all)
  async with SessionTest() as session:
    yield session
  await engine.dispose()



@pytest_asyncio.fixture
async def user(db_session):
  user = User(username='pawlo', hashed_password=hash_value('34f432'), email='eryk123@gm.com', user_id=1)
  db_session.add(user)
  await db_session.commit()
  return user

@pytest_asyncio.fixture
async def admin(db_session):
  user = User(username='adam', hashed_password=hash_value('ddddd'), email='adamek23@gm.com', user_id=2)
  db_session.add(user)
  user_roles = UserRoles(user_id=2, roles = [Role.USER, Role.ADMIN], version=1)
  db_session.add(user_roles)
  await db_session.commit()
  return user

@pytest_asyncio.fixture
async def product_editor(db_session):
  user = User(username='edyta', hashed_password=hash_value('eeee'), email='edzia23@gm.com', user_id=3)
  db_session.add(user)
  user_roles = UserRoles(user_id=3, roles = [Role.USER, Role.PRODUCT_EDITOR], version=1)
  db_session.add(user_roles)
  await db_session.commit()
  return user



@pytest_asyncio.fixture
def user_repository(db_session):
  return SqlAlchemyUserRepository(db_session)

@pytest_asyncio.fixture
async def user_roles(db_session, user):
  user_roles = UserRoles(user_id=1, roles = [Role.USER, Role.PRODUCT_EDITOR], version=1)
  db_session.add(user_roles)
  await db_session.commit()
  return user_roles

@pytest_asyncio.fixture
def user_roles_repository(db_session):
  return SqlAlchemyUserRolesRepository(db_session)

@pytest_asyncio.fixture
def access_service(user_roles_repository):
  return AccessService(user_roles_repository)

@pytest_asyncio.fixture
def refresh_token_repository(db_session):
  return SqlAlchemyRefreshTokenRepository(db_session)

@pytest_asyncio.fixture
async def refresh_token(db_session, user):
  token = RefreshToken(token_hash='pik12', user_id=user.user_id, expires_at=datetime(2026, 8, 29, 18, 0, 0), revoked_at=None)
  db_session.add(token)
  await db_session.commit()
  return token

@pytest_asyncio.fixture
async def redis_client():
  client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
  await client.flushdb()
  yield client
  await client.aclose()

@pytest_asyncio.fixture
async def example_session(redis_client):
  session = Session(1, SessionData(123, 'Jan'))
  key = f'session:{session.session_id}'
  await redis_client.hset(
    key, 
    mapping={
      'user_id': session.session_data.user_id,
      'username':session.session_data.username, 
    }) 
  await redis_client.expire(key,  60 * 60 * 24 * 7)
  return session

@pytest.fixture
def unit_of_work_factory(db_session, redis_client):
  return DefaultUnitOfWorkFactory(db_session, redis_client)

@pytest.fixture
def redis_uow(redis_client):
  return RedisUnitOfWork(redis_client)

@pytest.fixture
def sql_uow(db_session):
  return SqlAlchemyUnitOfWork(db_session)

@pytest_asyncio.fixture
async def session_repository(redis_client):
  return RedisSessionRepository(redis_client)

@pytest_asyncio.fixture
async def user_roles_cache(redis_client):
  return RedisUserRolesCache(redis_client)


@pytest_asyncio.fixture
async def example_roles(redis_client):
  user_roles_key = f'user_roles:{123}'
  roles = [Role.USER, Role.PRODUCT_EDITOR]
  await redis_client.hset(
    user_roles_key, 
    mapping={
      'roles': json.dumps(roles)
    }) 
  await redis_client.expire(user_roles_key,  60 * 60 * 24 * 7)
  return roles

@pytest_asyncio.fixture
async def session_authentication_provider(redis_uow):
  return SessionAuthenticationProvider(redis_uow)

@pytest_asyncio.fixture
async def jwt_authentication_provider(sql_uow):
  return JwtAuthenticationProvider(sql_uow)

@pytest_asyncio.fixture
def authentication_provider_factory(unit_of_work_factory):
  return DefaultAuthenticationProviderFactory(unit_of_work_factory)

@pytest.fixture
def authentication_service(authentication_provider_factory, user_repository):
  return AuthenticationService(authentication_provider_factory, user_repository)



