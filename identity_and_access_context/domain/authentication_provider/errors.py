class AuthenticationProviderError(Exception):
  pass

class CredentialNotFound(AuthenticationProviderError):
  pass

class InvalidCredential(AuthenticationProviderError):
  pass
