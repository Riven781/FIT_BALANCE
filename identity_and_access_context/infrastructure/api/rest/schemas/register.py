from pydantic import BaseModel

from identity_and_access_context.application.command.register import RegisterCommand


class RegisterRequest(BaseModel):
  username: str
  password: str
  password_repeated: str
  email: str

  def to_command(self) -> RegisterCommand:
    return RegisterCommand(self.username, self.password, self.password_repeated, self.email)