class ServiceError(Exception):
  pass

class InvalidCredentialsError(ServiceError):
  pass

class PasswordsMustBeTheSame(ServiceError):
  pass

class EmailAlreadyExists(ServiceError):
  pass

class UsernameAlreadyExists(ServiceError):
  pass

class InsufficientPermissions(ServiceError):
  pass

class AuthenticationRequired(ServiceError):
  pass

class UserNotFoundError(ServiceError):
  pass

class AmbiguousAuthentication(ServiceError):
  pass

class UserRolesChangedSinceRead(ServiceError):
  pass