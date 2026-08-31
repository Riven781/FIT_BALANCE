import pytest
from identity_and_access_context.application.user_roles_management_serivce import UserRolesManagementService
from identity_and_access_context.domain.role import Role
from identity_and_access_context.application.errors import UserNotFoundError
from identity_and_access_context.application.errors import InsufficientPermissions

@pytest.mark.asyncio
async def test_set_roles_by_admin(user_roles_repository, sql_uow, access_service, admin, product_editor, db_session):
  user_management_service = UserRolesManagementService(sql_uow, access_service)
  await user_management_service.set_roles(admin.user_id, product_editor.user_id, [Role.USER, Role.MODERATOR])
  #await db_session.commit()
  user_roles = await user_roles_repository.get_by_user_id(product_editor.user_id)
  assert len(user_roles.roles) == 2
  assert Role.USER in user_roles.roles
  assert Role.MODERATOR in user_roles.roles

@pytest.mark.asyncio
async def test_set_roles_by_admin_for_not_existing_user(sql_uow, access_service, admin):
  user_management_service = UserRolesManagementService(sql_uow, access_service)
  with pytest.raises(UserNotFoundError):
    await user_management_service.set_roles(admin.user_id, 1000, [Role.USER, Role.MODERATOR])


@pytest.mark.asyncio
async def test_set_roles_by_not_admin_for_not_existing_user(sql_uow, access_service, product_editor, user):
  user_management_service = UserRolesManagementService(sql_uow, access_service)
  with pytest.raises(InsufficientPermissions):
    await user_management_service.set_roles(user.user_id, product_editor.user_id, [Role.USER, Role.MODERATOR])
  