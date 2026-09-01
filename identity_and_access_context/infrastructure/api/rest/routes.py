from typing import Annotated

from fastapi import APIRouter, Body, Cookie, Depends, Header, Response, status
from fastapi.security import OAuth2PasswordBearer

from identity_and_access_context.application.authentication_service import AuthenticationService
from identity_and_access_context.application.command.login import LoginCommand
from identity_and_access_context.application.user_management_service import UserManagementService
from identity_and_access_context.application.user_roles_management_serivce import UserRolesManagementService
from identity_and_access_context.domain.auth_credentials.jwt_credential import JwtAccessTokenCredential, JwtCredential, JwtRefreshTokenCredential
from identity_and_access_context.domain.auth_credentials.session_credential import SessionCredential
from identity_and_access_context.domain.auth_method import AuthMethod
from identity_and_access_context.infrastructure.api.rest.dependencies import get_authentication_credential, get_authentication_service, get_current_user, get_user_management_service, get_user_roles_management_service
from identity_and_access_context.infrastructure.api.rest.schemas.login import LoginRequest
from identity_and_access_context.infrastructure.api.rest.schemas.register import RegisterRequest
from identity_and_access_context.infrastructure.api.rest.schemas.roles import SetRolesRequest
from identity_and_access_context.infrastructure.api.rest.schemas.tokens import LoggedInMessage, RefreshJwtRequest, TokensResponse


identity_and_access_context_router = APIRouter()

@identity_and_access_context_router.post("/login/session", status_code=status.HTTP_204_NO_CONTENT)
async def login_session(
  credentials: LoginRequest, 
  authentication_service: Annotated[AuthenticationService, Depends(get_authentication_service)],
  response: Response
) -> None:
  authentication_credential = await authentication_service.login(LoginCommand(auth_method=AuthMethod.SESSION, username=credentials.username, password=credentials.password))
  response.set_cookie(
    key="session_id",
    value=authentication_credential.session_id,
    httponly=True,
    secure=True,
    samesite='lax',
    max_age=authentication_credential.ttl
  )

@identity_and_access_context_router.post("/login/jwt", status_code=status.HTTP_200_OK)
async def login_jwt(
  credentials: LoginRequest, 
  authentication_service: Annotated[AuthenticationService, Depends(get_authentication_service)],
) -> TokensResponse:
  tokens = await authentication_service.login(LoginCommand(auth_method=AuthMethod.JWT, username=credentials.username, password=credentials.password))
  return tokens

@identity_and_access_context_router.post("/logout/session", status_code=status.HTTP_204_NO_CONTENT)
async def logout_session(
  session_id: Annotated[str, Cookie()],
  authentication_service: Annotated[AuthenticationService, Depends(get_authentication_service)],
  response: Response
) -> None:
  await authentication_service.logout(SessionCredential(session_id))
  response.delete_cookie("session_id")

oauth2_schema = OAuth2PasswordBearer(tokenUrl="login", auto_error=False)


@identity_and_access_context_router.post("/logout/jwt", status_code=status.HTTP_204_NO_CONTENT)
async def logout_jwt(
  request: RefreshJwtRequest,
  authentication_service: Annotated[AuthenticationService, Depends(get_authentication_service)],
):
  await authentication_service.logout(JwtAccessTokenCredential(request.refresh_token))


@identity_and_access_context_router.post("/refresh/session", status_code=status.HTTP_204_NO_CONTENT)
async def refresh_session(
  session_id: Annotated[str, Cookie()], 
  authentication_service: Annotated[AuthenticationService, Depends(get_authentication_service)],
  response: Response
) -> None:
  session = await authentication_service.refresh(SessionCredential(session_id))
  response.set_cookie(
      key="session_id",
      value=session.session_id,
      httponly=True,
      secure=True,
      samesite='lax',
      max_age=session.ttl
    )


@identity_and_access_context_router.post("/refresh/jwt", status_code=status.HTTP_200_OK)
async def refresh_jwt(
  request: RefreshJwtRequest, 
  authentication_service: Annotated[AuthenticationService, Depends(get_authentication_service)],
) -> TokensResponse:
  tokens = await authentication_service.refresh(JwtRefreshTokenCredential(request.refresh_token))
  return tokens


@identity_and_access_context_router.post("/register",status_code=status.HTTP_204_NO_CONTENT)
async def register(
  credentials: Annotated[RegisterRequest, Body()],
  user_management_service: Annotated[UserManagementService, Depends(get_user_management_service)]
):
  await user_management_service.register(credentials.to_command())


@identity_and_access_context_router.put("/users/{user_id}/roles/", status_code=status.HTTP_204_NO_CONTENT)
async def set_roles(
  user_id: int,
  admin_id: Annotated[int, Depends(get_current_user)],
  request: SetRolesRequest,
  service: Annotated[UserRolesManagementService, Depends(get_user_roles_management_service)]
) -> None:
  await service.set_roles(admin_id, user_id, request.roles)