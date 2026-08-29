import pytest
from identity_and_access_context.domain.user.user import User
from identity_and_access_context.domain.role import Role
from identity_and_access_context.domain.authentication_provider.errors import CredentialNotFound

@pytest.mark.asyncio
async def test_login(session_authentication_provider, session_repository):
  user = User(user_id=10, username='wolek123', hashed_password='haslo', email='wol123@gmail.com')
  session = await session_authentication_provider.login(user)
  assert session is not None
  session = await session_repository.get_by_id(session.session_id)
  assert session.session_data.user_id == 10
  assert session.session_data.username == 'wolek123'

@pytest.mark.asyncio
async def test_logout_not_existing_session(session_authentication_provider):
  with pytest.raises(CredentialNotFound):
    await session_authentication_provider.logout(10)

@pytest.mark.asyncio
async def test_logout(session_authentication_provider, session_repository, example_session):
  await session_authentication_provider.logout(1)
  session = await session_repository.get_by_id(1)
  assert session is None

@pytest.mark.asyncio
async def test_authenticate(session_authentication_provider, example_session):
  authenticated_user_id = await session_authentication_provider.authenticate(1)
  assert authenticated_user_id == 123


@pytest.mark.asyncio
async def test_authenticate_not_existing_session(session_authentication_provider):
  with pytest.raises(CredentialNotFound):
    authenticated_user_id = await session_authentication_provider.authenticate(10)

@pytest.mark.asyncio
async def test_refresh_session(session_authentication_provider, example_session):
  session = await session_authentication_provider.refresh(1)
  assert session.ttl == 60 * 60 * 24 * 37

@pytest.mark.asyncio
async def test_refreshnot_existing_session(session_authentication_provider):
  with pytest.raises(CredentialNotFound):
    session = await session_authentication_provider.refresh(10)
 