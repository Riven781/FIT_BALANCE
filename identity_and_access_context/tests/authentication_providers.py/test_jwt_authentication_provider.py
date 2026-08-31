import pytest
from identity_and_access_context.domain.user.user import User
from identity_and_access_context.domain.role import Role
from identity_and_access_context.infrastructure.security import hash_value
from identity_and_access_context.domain.authentication_provider.errors import CredentialNotFound, InvalidCredential
import time

@pytest.mark.asyncio
async def test_login(jwt_authentication_provider, user, refresh_token_repository):
  tokens = await jwt_authentication_provider.login(user)
  assert tokens is not None
  assert tokens.access_token is not None
  assert tokens.refresh_token is not None

  refresh_token = await refresh_token_repository.get_by_hash(hash_value(tokens.refresh_token))
  assert refresh_token.user_id == user.user_id

@pytest.mark.asyncio
async def test_logout_not_existing_refresh_token(jwt_authentication_provider):
  await jwt_authentication_provider.logout('bad_token')

@pytest.mark.asyncio
async def test_login_and_logout(jwt_authentication_provider, user, refresh_token, refresh_token_repository):
  tokens = await jwt_authentication_provider.login(user)
  await jwt_authentication_provider.logout(tokens.refresh_token)
  refresh_token = await refresh_token_repository.get_by_hash(hash_value(tokens.refresh_token))
  assert refresh_token is None

@pytest.mark.asyncio
async def test_login_and_authenticate(jwt_authentication_provider, user):
  tokens = await jwt_authentication_provider.login(user)
  authenticated_user_id = await jwt_authentication_provider.authenticate(tokens.access_token)
  assert authenticated_user_id == user.user_id

@pytest.mark.asyncio
async def test_authenticate_bad_access_token(jwt_authentication_provider):
  with pytest.raises(InvalidCredential):
    authenticated_user_id = await jwt_authentication_provider.authenticate('bad_token')

@pytest.mark.asyncio
async def test_refresh_token(jwt_authentication_provider, user):
  tokens = await jwt_authentication_provider.login(user)
  time.sleep(1)
  new_tokens = await jwt_authentication_provider.refresh(tokens.refresh_token)
  assert new_tokens.access_token != tokens.access_token
  assert new_tokens.refresh_token == tokens.refresh_token

@pytest.mark.asyncio
async def test_refresh_using_bad_refresh_token(jwt_authentication_provider, user):
  tokens = await jwt_authentication_provider.login(user)
  time.sleep(1)
  with pytest.raises(CredentialNotFound):
    new_tokens = await jwt_authentication_provider.refresh('bad token')


@pytest.mark.asyncio
async def test_authenticate_by_expired_token(jwt_authentication_provider, user):
  token_value = jwt_authentication_provider._create_access_token(user.user_id, seconds=1)
  time.sleep(2)
  with pytest.raises(InvalidCredential):
    authenticated_user_id = await jwt_authentication_provider.authenticate(token_value)

@pytest.mark.asyncio
async def test_logout_by_expired_refesh_token_token(jwt_authentication_provider, user):
  token_value = await jwt_authentication_provider._create_refresh_token(user.user_id, seconds=1)
  time.sleep(2)
  await jwt_authentication_provider.logout(token_value)

@pytest.mark.asyncio
async def test_refresh_by_expired_token(jwt_authentication_provider, user):
  refresh_token_value = await jwt_authentication_provider._create_refresh_token(user.user_id, seconds=1)
  time.sleep(3)
  with pytest.raises(InvalidCredential):
    tokens = await jwt_authentication_provider.refresh(refresh_token_value)

@pytest.mark.asyncio
async def test_refresh_two_tokens(jwt_authentication_provider, user):
  refresh_token_value = await jwt_authentication_provider._create_refresh_token(user.user_id, seconds=10) #lifetime of refresh token is low so client will get new one
  new_tokens = await jwt_authentication_provider.refresh(refresh_token_value)
  assert new_tokens.refresh_token != refresh_token_value
  assert new_tokens.access_token is not None