import aiosqlite

from api.repository.errors.errors import CheckViolationError, ForeignKeyViolationError, NotNullViolationError, RepositoryError, RepositoryIntegrityError, RepositoryProgrammingError, RepositoryUnavailableError, UniqueViolationError, UnknownRepositoryError

def map_errors(e):
  if isinstance(e, aiosqlite.Error):
    error_name = getattr(e, "sqlite_errorname", None)
    if isinstance(e, aiosqlite.IntegrityError):
      if error_name in ("SQLITE_CONSTRAINT_UNIQUE", "SQLITE_CONSTRAINT_PRIMARYKEY"):
        return UniqueViolationError()
      if error_name == "SQLITE_CONSTRAINT_FOREIGNKEY":
        return ForeignKeyViolationError()
      if error_name == "SQLITE_CONSTRAINT_NOTNULL":
        return NotNullViolationError()
      if error_name == "SQLITE_CONSTRAINT_CHECK":
        return CheckViolationError()
      return RepositoryIntegrityError()
    if isinstance(e, aiosqlite.OperationalError):
      if error_name in ("SQLITE_BUSY", "SQLITE_LOCKED"):
        return RepositoryUnavailableError()
      return RepositoryProgrammingError()
    if isinstance(e, aiosqlite.ProgrammingError):
      return RepositoryProgrammingError()
    
    return RepositoryError()
  else:
    return UnknownRepositoryError()
    