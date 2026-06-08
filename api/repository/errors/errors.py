
class RepositoryError(Exception):
  pass



class RepositoryOperationalError(RepositoryError):
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


class RepositoryUnavailableError(RepositoryError):
  pass

class RepositoryConnectionError(RepositoryError):
  pass


class RepositoryProgrammingError(RepositoryError):
  pass



class UnknownRepositoryError(RepositoryError):
  pass