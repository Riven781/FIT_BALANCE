from fastapi import Request
from fastapi.responses import JSONResponse

from api.repository.errors.errors import RepositoryError


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
