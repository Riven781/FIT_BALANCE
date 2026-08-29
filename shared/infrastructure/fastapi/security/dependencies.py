from typing import Annotated
from fastapi import Cookie, Depends, Header
from fastapi.security import OAuth2PasswordBearer
from shared.infrastructure.fastapi.security.contracts import AuthMethod, RawAuthenticationCredentials



oauth2_schema = OAuth2PasswordBearer(tokenUrl="login", auto_error=False)

async def get_raw_authentication_credentials(
    #auth_method: Annotated[AuthMethod, Header(alias='X-Auth-Method')],
    session_id: Annotated[str | None, Cookie()] = None,
    token: Annotated[str | None, Depends(oauth2_schema)] = None
) -> RawAuthenticationCredentials:
  return RawAuthenticationCredentials(session_id=session_id, token=token)