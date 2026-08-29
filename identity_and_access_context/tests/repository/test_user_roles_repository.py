import pytest
from identity_and_access_context.domain.role import Role
from identity_and_access_context.domain.user_roles.user_roles import UserRoles


@pytest.mark.asyncio
async def test_get_by_user_id(user_roles_repository, user_roles):
  user_roles = await user_roles_repository.get_by_user_id(user_roles.user_id)
  assert user_roles.user_id == 1
  assert user_roles.version == 1
  assert len(user_roles.roles) == 2
  assert Role.USER in user_roles.roles
  assert Role.PRODUCT_EDITOR in user_roles.roles


@pytest.mark.asyncio
async def test_get_by_not_existing_user_id(user_roles_repository):
  user_roles = await user_roles_repository.get_by_user_id(1000)
  assert user_roles is None


@pytest.mark.asyncio
async def test_save_new_user_roles(user_roles_repository, user, db_session):
  user_roles = UserRoles(user_id=user.user_id, roles=[Role.CATALOG_MANAGER, Role.MODERATOR])
  await user_roles_repository.save(user_roles)
  #await db_session.commit()
  user_roles_from_fb = await user_roles_repository.get_by_user_id(user_roles.user_id)
  assert user_roles_from_fb.user_id == 1
  assert user_roles_from_fb.version == 1
  assert len(user_roles_from_fb.roles) == 2
  assert Role.MODERATOR in user_roles_from_fb.roles
  assert Role.CATALOG_MANAGER in user_roles_from_fb.roles


@pytest.mark.asyncio
async def test_save_existing_user_roles(user_roles_repository, user_roles, db_session):
  user_roles = await user_roles_repository.get_by_user_id(user_roles.user_id)
  user_roles.remove_role(Role.PRODUCT_EDITOR)
  user_roles.add_role(Role.ADMIN)
  await user_roles_repository.save(user_roles)
  #await db_session.commit()
  user_roles_from_fb = await user_roles_repository.get_by_user_id(user_roles.user_id)
  assert user_roles_from_fb.user_id == 1
  assert user_roles_from_fb.version == 2
  assert len(user_roles_from_fb.roles) == 2
  assert Role.PRODUCT_EDITOR not in user_roles_from_fb.roles
  assert Role.ADMIN in user_roles_from_fb.roles
  assert Role.USER in user_roles_from_fb.roles