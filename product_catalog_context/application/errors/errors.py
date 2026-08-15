


class ServiceError(Exception):
  pass

class ProductNotFoundError(ServiceError):
  pass

class ProductAlreadyExistsError(ServiceError):
  pass

class InvalidProductDataError(ServiceError):
  pass

class InvalidProductCategoryId(ServiceError):
  pass

#hierarchy
class DraftCategoryHierarchyExists(ServiceError):
  pass

class CategoryDoesNotBelongToHierarchy(ServiceError): #move to domain error
  pass

class CategoryHierarchyDoesNotExist(ServiceError):
  pass


#assignment
class TaskDoesNotExist(ServiceError):
  pass

class TasksBelongToDifferentHierarchies(ServiceError):
  pass
    