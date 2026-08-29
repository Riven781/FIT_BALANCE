import pytest
from identity_and_access_context.domain.role import Role
from identity_and_access_context.application.errors import InsufficientPermissions


@pytest.mark.asyncio
async def test_authorize_user_with_his_role(access_service, user_roles):
  await access_service.authorize(user_roles.user_id, Role.USER)

@pytest.mark.asyncio
async def test_authorize_user_without_his_role(access_service, user_roles):
  with pytest.raises(InsufficientPermissions):
    await access_service.authorize(user_roles.user_id, Role.MODERATOR)

@pytest.mark.asyncio
async def test_authorize_not_existing_user(access_service):
  with pytest.raises(InsufficientPermissions):
    await access_service.authorize(100, Role.USER)