import pytest
from  identity_and_access_context.application.authentication_service import AuthenticationService
from identity_and_access_context.application.errors import  EmailAlreadyExists, InvalidCredentialsError, PasswordsMustBeTheSame, UsernameAlreadyExists
from identity_and_access_context.application.errors import  EmailAlreadyExists, InvalidCredentialsError, PasswordsMustBeTheSame, UsernameAlreadyExists
from identity_and_access_context.domain.auth_method import AuthMethod
from identity_and_access_context.application.command.login import LoginCommand

@pytest.mark.asyncio
async def test_login_not_existing_user_with_session(authentication_provider_factory, user_repository):
  authentication_service = AuthenticationService(authentication_provider_factory, user_repository)
  with pytest.raises(InvalidCredentialsError):
    session_id = await authentication_service.login(LoginCommand(AuthMethod.SESSION, 'olek', 'password'))


@pytest.mark.asyncio
async def test_login_existing_user_with_session(authentication_provider_factory, user_repository, user):
  authentication_service = AuthenticationService(authentication_provider_factory, user_repository)
  session_id = await authentication_service.login(LoginCommand(AuthMethod.SESSION, 'pawlo', '34f432'))
  assert session_id is not None


@pytest.mark.asyncio
async def test_login_not_existing_user_with_jwt(authentication_provider_factory, user_repository):
  authentication_service = AuthenticationService(authentication_provider_factory, user_repository)
  with pytest.raises(InvalidCredentialsError):
    tokens = await authentication_service.login(LoginCommand(AuthMethod.JWT, 'olek', 'password'))

@pytest.mark.asyncio
async def test_login_existing_user_with_jwt(authentication_provider_factory, user_repository, user):
  authentication_service = AuthenticationService(authentication_provider_factory, user_repository)
  tokens = await authentication_service.login(LoginCommand(AuthMethod.JWT, 'pawlo', '34f432'))
  assert tokens is not None