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
  with pytest.raises(CredentialNotFound):
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
async def test_refresh__using_bad_refresh_token(jwt_authentication_provider, user):
  tokens = await jwt_authentication_provider.login(user)
  time.sleep(1)
  with pytest.raises(CredentialNotFound):
    new_tokens = await jwt_authentication_provider.refresh('bad token')
