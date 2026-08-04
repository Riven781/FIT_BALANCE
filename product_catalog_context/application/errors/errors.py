

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



    