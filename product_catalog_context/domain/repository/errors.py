class RepositoryError(Exception):
  pass

class RepositoryIntegrityError(RepositoryError):
  pass

class UniqueViolationError(RepositoryIntegrityError):
  pass

class ForeignKeyViolationError(RepositoryIntegrityError):
  pass

class NotNullViolationError(RepositoryIntegrityError):
  pass

class CheckViolationError(RepositoryIntegrityError):
  pass

class TypeViolationError(RepositoryIntegrityError):
  pass

class RepositoryUnavailableError(RepositoryError):
  pass

class RepositoryProgrammingError(RepositoryError):
  pass

class UnknownRepositoryError(RepositoryError):
  pass

class ConcurrentModification(RepositoryIntegrityError):
  pass
