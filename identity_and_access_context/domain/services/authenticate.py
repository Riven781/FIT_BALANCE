from identity_and_access_context.domain.services.encrypt_value import encrypt_value


def authenticate(username, password: str, user_repository):
  if username is None:
    raise ValueError()
  if password is None:
    raise ValueError()

  encrypted_password = encrypt_value(password)

  user = user_repository.user_from_authentic_credentials(username, encrypted_password)

  return user

