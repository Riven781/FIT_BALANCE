from identity_and_access_context.application.command.register import RegisterCommand
from identity_and_access_context.application.errors import  AuthenticationRequired, EmailAlreadyExists, InvalidCredentialsError, PasswordsMustBeTheSame, UsernameAlreadyExists
from identity_and_access_context.domain.user.user import User
from identity_and_access_context.infrastructure.security import hash_value


class UserManagementService: #change password, register exc
  def __init__(self, user_repository):
    self.user_repository = user_repository

  async def register(self, registration_command: RegisterCommand):
    if registration_command.password != registration_command.password_repeated:
      raise PasswordsMustBeTheSame()
    if await self.user_repository.exists_by_email(registration_command.email):
      raise EmailAlreadyExists()
    if await self.user_repository.exists_by_username(registration_command.username):
      raise UsernameAlreadyExists()
    user = User(username=registration_command.username, hashed_password=hash_value(registration_command.password), email=registration_command.email)
    await self.user_repository.save(user)