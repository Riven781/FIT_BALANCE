class RepositoryError(Exception):
  pass

class ConcurrentModification(RepositoryError):
  pass

