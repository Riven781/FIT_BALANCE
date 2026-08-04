from fastapi import Request
from fastapi.responses import JSONResponse

from product_catalog_context.infrastructure.aiosqlite_repository.errors.errors import RepositoryError
from product_catalog_context.application.errors.errors import InvalidProductCategoryId, InvalidProductDataError, ProductAlreadyExistsError, ProductNotFoundError

def register_exception_handlers(app):
  app.add_exception_handler(RepositoryError, repository_error_handler)
  app.add_exception_handler(ProductNotFoundError, product_not_found_handler)
  app.add_exception_handler(InvalidProductDataError, invalid_product_data_handler)
  app.add_exception_handler(InvalidProductCategoryId, invalid_product_category_id_handler)
  app.add_exception_handler(ProductAlreadyExistsError, product_already_exists_handler)


async def repository_error_handler(request: Request, exc: RepositoryError):
  return JSONResponse(
    status_code=500,
    content={
      "message": 'Internal Server Error'
    }
  )

async def product_not_found_handler(req, exc):
  return JSONResponse(
    status_code=404,
    content={
      "message": "Not Found"
    }
  )

async def invalid_product_data_handler(req, exc):
  return JSONResponse(
    status_code=400,
    content={
      "message": "Bad Request"
    }
  )

async def invalid_product_category_id_handler(req, exc):
  return JSONResponse(
    status_code=404,
    content={
      "message": "Not Found",
      "detail" : "Product category doesn't exist."
    }
  )

async def product_already_exists_handler(req, exc):
  return JSONResponse(
    status_code=409,
    content={
      "message": "Conflict"
    }
  )
