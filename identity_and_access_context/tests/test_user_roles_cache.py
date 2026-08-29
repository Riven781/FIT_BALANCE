import pytest
from identity_and_access_context.domain.role import Role

@pytest.mark.asyncio
async def test_get(user_roles_cache, example_roles):
  roles = await user_roles_cache.get(123)
  assert len(roles) == 2
  assert  Role.USER in roles
  assert  Role.PRODUCT_EDITOR in roles

@pytest.mark.asyncio
async def test_get_not_existing_roles(user_roles_cache):
  roles = await user_roles_cache.get(123)
  assert roles is None


@pytest.mark.asyncio
async def test_set(user_roles_cache):
  await user_roles_cache.set(1, [Role.USER])
  roles = await user_roles_cache.get(1)
  assert len(roles) == 1
  assert  Role.USER in roles

@pytest.mark.asyncio
async def test_invalidate(user_roles_cache, example_roles):
  await user_roles_cache.invalidate(123)
  roles = await user_roles_cache.get(123)
  assert roles is None
