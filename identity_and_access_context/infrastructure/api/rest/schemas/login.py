from pydantic import BaseModel
from identity_and_access_context.application.command.login import LoginCommand
from identity_and_access_context.domain.auth_method import AuthMethod


class LoginRequest(BaseModel):
  username: str
  password: str
