from fastapi.responses import JSONResponse

from identity_and_access_context.application.errors import AmbiguousAuthentication, AuthenticationRequired, EmailAlreadyExists, InsufficientPermissions, PasswordsMustBeTheSame, UserNotFoundError, UserRolesChangedSinceRead, UsernameAlreadyExists, InvalidCredentialsError
from identity_and_access_context.domain.authentication_provider.errors import InvalidCredential
from identity_and_access_context.domain.repository.errors import RepositoryError


def register_identity_and_access_exception_handlers(app):
  app.add_exception_handler(RepositoryError, repository_error_handler)
  app.add_exception_handler(InvalidCredentialsError, invalid_credentials_handler)
  app.add_exception_handler(AuthenticationRequired, authentication_required_handler)
  app.add_exception_handler(AmbiguousAuthentication, ambiguous_authentication_handler)
  app.add_exception_handler(InsufficientPermissions, insufficient_permissions_handler)
  app.add_exception_handler(EmailAlreadyExists, email_already_exists_handler)
  app.add_exception_handler(UsernameAlreadyExists, username_already_exists_handler)
  app.add_exception_handler(UserRolesChangedSinceRead, user_roles_changed_since_read_handler)
  app.add_exception_handler(UserNotFoundError, user_not_found_handler)
  app.add_exception_handler(PasswordsMustBeTheSame, passwords_must_be_the_same_handler)


def repository_error_handler(req, exc: RepositoryError):
  return JSONResponse(
    status_code=500,
    content={
      "message": "Internal Server Error"
    }
  )

def invalid_credentials_handler(req, exc: InvalidCredentialsError):
  return JSONResponse(
    status_code=401,
    content={
      "message": "Invalid credentials"
    }
  )

def authentication_required_handler(req, exc: AuthenticationRequired):
  return JSONResponse(
    status_code=401,
    content={
      "message": "Authentication required"
    }
  )

def ambiguous_authentication_handler(req, exc: AmbiguousAuthentication):
  return JSONResponse(
    status_code=401,
    content={
      "message": "Multiple authentication methods provided"
    }
  )

def insufficient_permissions_handler(req, exc: InsufficientPermissions):
  return JSONResponse(
    status_code=403,
    content={
      "message": "Insufficient permissions"
    }
  )

def email_already_exists_handler(req, exc: EmailAlreadyExists):
  return JSONResponse(
    status_code=409,
    content={
      "message" : "Email already exists"
    }
  )


def username_already_exists_handler(req, exc: UsernameAlreadyExists):
  return JSONResponse(
    status_code=409,
    content={
      "message" : "Username already exists"
    }
  )

def user_roles_changed_since_read_handler(req, exc: UserRolesChangedSinceRead):
  return JSONResponse(
    status_code=409,
    content={
      "message" : "User roles have changed since they were last read"
    }
  )

def user_not_found_handler(req, exc: UserNotFoundError):
  return JSONResponse(
    status_code=404,
    content={
      "message": "User not found"
    }
  )

def passwords_must_be_the_same_handler(req, exc: PasswordsMustBeTheSame):
  return JSONResponse(
    status_code=422,
    content={
      "message": "Passwords must be the same"
    }
  )