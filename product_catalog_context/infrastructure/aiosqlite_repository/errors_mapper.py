import aiosqlite

from product_catalog_context.infrastructure.aiosqlite_repository.errors.errors import CheckViolationError, ForeignKeyViolationError, NotNullViolationError, RepositoryError, RepositoryIntegrityError, RepositoryProgrammingError, RepositoryUnavailableError, TypeViolationError, UniqueViolationError, UnknownRepositoryError

def map_errors(e):
  if isinstance(e, aiosqlite.Error):
    error_name = getattr(e, "sqlite_errorname", None)
    error_code = getattr(e, "sqlite_errorcode", None)
    if isinstance(e, aiosqlite.IntegrityError):
      if error_code == 3091:
        return TypeViolationError()
      if error_name in ("SQLITE_CONSTRAINT_UNIQUE", "SQLITE_CONSTRAINT_PRIMARYKEY"):
        return UniqueViolationError()
      if error_name == "SQLITE_CONSTRAINT_FOREIGNKEY":
        return ForeignKeyViolationError()
      if error_name == "SQLITE_CONSTRAINT_NOTNULL":
        return NotNullViolationError()
      if error_name == "SQLITE_CONSTRAINT_CHECK":
        return CheckViolationError()
      return RepositoryIntegrityError('Repository Integrity Error')
    if isinstance(e, aiosqlite.OperationalError):
      if error_name in ("SQLITE_BUSY", "SQLITE_LOCKED"):
        return RepositoryUnavailableError()
      return RepositoryProgrammingError()
    if isinstance(e, aiosqlite.ProgrammingError):
      return RepositoryProgrammingError()
    
    return RepositoryError()
  else:
    return UnknownRepositoryError()
    