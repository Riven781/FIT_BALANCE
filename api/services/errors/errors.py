

class ServiceError(Exception):
  pass

class ProductNotFoundError(ServiceError):
  pass

class ProductAlreadyExistError(ServiceError):
  pass
  
class CannotDeleteProductError(ServiceError):
  pass

class InvalidProductDataError(ServiceError):
  pass

class InvalidProductCategoryId(ServiceError):
  pass



    