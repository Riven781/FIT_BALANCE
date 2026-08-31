import pytest
from identity_and_access_context.application.user_management_service import UserManagementService
from identity_and_access_context.domain.auth_method import AuthMethod
from identity_and_access_context.application.errors import EmailAlreadyExists, InvalidCredentialsError, PasswordsMustBeTheSame, UsernameAlreadyExists
from identity_and_access_context.application.command.register import RegisterCommand
from identity_and_access_context.application.command.login import LoginCommand


@pytest.mark.asyncio
async def test_register_new_user(sql_uow, authentication_service):
  user_management_service = UserManagementService(sql_uow)
  registration_command = RegisterCommand('olek', 'password', 'password', 'olek@123')
  await user_management_service.register(registration_command)

  login_command = LoginCommand(AuthMethod.SESSION, username='olek', password='password')
  session_id = await authentication_service.login(login_command)
  assert session_id is not None

@pytest.mark.asyncio
async def test_register_with_existing_username(sql_uow, user):
  user_management_service = UserManagementService(sql_uow)
  registration_command = RegisterCommand('pawlo', 'password', 'password', 'olek@123')
  with pytest.raises(UsernameAlreadyExists):
    await user_management_service.register(registration_command)