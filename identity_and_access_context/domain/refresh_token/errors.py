from product_catalog_context.domain.errors import DomainError


class RefreshTokenAlreadyRevoked(DomainError):
  pass

class RefreshTokenExpired(DomainError):
  pass