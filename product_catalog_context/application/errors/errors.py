


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

class CategoryDoesNotBelongToActiveHierarchy(ServiceError): #move to domain error
  pass

class CategoryDoesNotBelongToPlannedHierarchy(ServiceError): #move to domain error
  pass

class CategoryHierarchyDoesNotExist(ServiceError):
  pass

class PlannedHierarchyDoesNotExist(ServiceError):
  pass

#assignment
class TaskDoesNotExist(ServiceError):
  pass

class TasksBelongToDifferentHierarchies(ServiceError):
  pass


class UserIdRequired(ServiceError):
  pass

class TaskNotFoundError(ServiceError):
  pass

class IssueNotFoundError(ServiceError):
  pass

class AccessDenied(ServiceError):
  pass

class CategoryAssignmentBelongsToAnotherUser(ServiceError):
  pass

class CategoryAssignmentRequiresProductEditor(ServiceError):
  pass