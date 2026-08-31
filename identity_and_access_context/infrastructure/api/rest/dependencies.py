from typing import Annotated
from fastapi import Cookie, Depends, Header
from fastapi.security import OAuth2PasswordBearer
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from identity_and_access_context.application.access_service import AccessService
from identity_and_access_context.application.authentication_service import AuthenticationService
from identity_and_access_context.application.unit_of_work.unit_of_work import UnitOfWork
from identity_and_access_context.application.unit_of_work.unit_of_work_factory import UnitOfWorkFactory
from identity_and_access_context.application.user_management_service import UserManagementService
from identity_and_access_context.application.user_roles_management_serivce import UserRolesManagementService
from identity_and_access_context.domain.auth_method import AuthMethod
from identity_and_access_context.application.to_authentication_credential import to_authentication_credential
from identity_and_access_context.infrastructure.authentication_providers.authentication_provider_factory import DefaultAuthenticationProviderFactory
from identity_and_access_context.infrastructure.authentication_providers.jwt_authentication_provider import JwtAuthenticationProvider
from identity_and_access_context.infrastructure.redis_repository.session_repository import RedisSessionRepository
from identity_and_access_context.infrastructure.authentication_providers.session_authentication_provider import SessionAuthenticationProvider
from identity_and_access_context.infrastructure.redis_repository.unit_of_work import RedisUnitOfWork
from identity_and_access_context.infrastructure.sql_alchemy_repository.refresh_token_repository import SqlAlchemyRefreshTokenRepository
from identity_and_access_context.infrastructure.sql_alchemy_repository.unit_of_work import SqlAlchemyUnitOfWork
from identity_and_access_context.infrastructure.sql_alchemy_repository.user_repository import SqlAlchemyUserRepository
from identity_and_access_context.infrastructure.sql_alchemy_repository.user_roles_repository import SqlAlchemyUserRolesRepository
from identity_and_access_context.infrastructure.unit_of_work_factory import DefaultUnitOfWorkFactory
from shared.database.redis_client import get_redis
from shared.database.session import get_session
from shared.infrastructure.fastapi.security.contracts import RawAuthenticationCredentials
from shared.infrastructure.fastapi.security.dependencies import get_raw_authentication_credentials



def get_user_repository(session: Annotated[AsyncSession, Depends(get_session)]):
  return SqlAlchemyUserRepository(session)

def get_refresh_token_repository(session: Annotated[AsyncSession, Depends(get_session)]):
  return SqlAlchemyRefreshTokenRepository(session)

def get_jwt_authentication_provider(refresh_token_reposiory: Annotated[SqlAlchemyRefreshTokenRepository, Depends(get_refresh_token_repository)]):
  return JwtAuthenticationProvider(refresh_token_reposiory)

def get_session_repository(redis: Annotated[Redis, Depends(get_redis)]):
  return RedisSessionRepository(redis)

def get_session_authentication_provider(session_repository: Annotated[Redis, Depends(get_session_repository)]):
  return SessionAuthenticationProvider(session_repository)



oauth2_schema = OAuth2PasswordBearer(tokenUrl="login", auto_error=False)
"""
async def get_authentication_credential(
    auth_method: Annotated[AuthMethod, Header(alias='X-Auth-Method')],
    session_id: Annotated[str | None, Cookie()],
    token: Annotated[str | None, Depends(oauth2_schema)]
    ) -> int:
  if auth_method == AuthMethod.JWT:
    return token
  if auth_method == AuthMethod.SESSION:
    return session_id
  raise ValueError(f"UnsupportedAuthMethod: {auth_method}")
"""

"""
async def get_authenticated_user_id(
    authentication_service: Annotated[AuthenticationService, Depends(get_authentication_service)],
    authentication_credential: Annotated[str | None, Depends(get_authentication_credential)]
    ) -> int:
  return await authentication_service.authenticate(authentication_credential)
"""
def get_user_roles_repository(session: Annotated[AsyncSession, Depends(get_session)]):
  return SqlAlchemyUserRolesRepository(session=session)

def get_access_service(user_roles_repository: Annotated[SqlAlchemyUserRolesRepository, get_user_roles_repository]):
  return AccessService(user_roles_repository)

def get_ephemeral_unit_of_work(redis: Annotated[Redis, Depends(get_redis)]):
  return RedisUnitOfWork(redis)

def get_persistent_unit_of_work(session: Annotated[AsyncSession, Depends(get_session)]):
  return SqlAlchemyUnitOfWork(session)

def get_unit_of_work_factory(session: Annotated[AsyncSession, Depends(get_session)], redis: Annotated[Redis, Depends(get_redis)]):
  return DefaultUnitOfWorkFactory(session, redis)

def get_authentication_provider_factory(
    unit_of_work_factory: Annotated[UnitOfWorkFactory, Depends(get_unit_of_work_factory)]
):
  return DefaultAuthenticationProviderFactory(unit_of_work_factory)

def get_authentication_service(
    user_repository: Annotated[SqlAlchemyUserRepository, Depends(get_user_repository)],
    authentication_provider_factory: Annotated[DefaultAuthenticationProviderFactory, Depends(get_authentication_provider_factory)],
  ):
  return AuthenticationService(user_repository=user_repository, authentication_provider_factory=authentication_provider_factory)

#it will be used in routes
def get_authentication_credential(credentials: Annotated[RawAuthenticationCredentials, Depends(get_raw_authentication_credentials)]):
  return to_authentication_credential(credentials)

#it will be used in public rest api
def get_authentication_credential_2(credentials: Annotated[RawAuthenticationCredentials, Depends()]):
  return to_authentication_credential(credentials)


async def get_current_user( 
  authentication_service: Annotated[AuthenticationService, Depends(get_authentication_service)],
  authentication_credential: Annotated[str | None, Depends(get_authentication_credential)]):
    return await authentication_service.authenticate(authentication_credential)

async def get_user_management_service(
    unit_of_work : Annotated[UnitOfWork, Depends(get_persistent_unit_of_work)]
):
  return UserManagementService(unit_of_work)

async def get_user_roles_management_service(
    unit_of_work : Annotated[UnitOfWork, Depends(get_persistent_unit_of_work)],
    access_service: Annotated[AccessService, Depends(get_access_service)]
):
  return UserRolesManagementService(unit_of_work, access_service)