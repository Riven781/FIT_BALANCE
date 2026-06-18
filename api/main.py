from contextlib import asynccontextmanager
from enum import Enum
from os import name
import re
from unittest import result
import aiofiles
import asyncio
from fastapi.encoders import jsonable_encoder
from api.database.db import init_db, reset_db
from api.dependencies.database import get_product_repository, get_product_service
from api.dependencies.product import check_ids
from api.error_handlers import invalid_product_category_id_handler, invalid_product_data_handler, product_already_exists_handler, product_not_found_handler, repository_error_handler
from api.repository.aiosqlite.product import ProductRepository
from api.repository.errors.errors import RepositoryError
from api.services.errors.errors import InvalidProductCategoryId, InvalidProductDataError, ProductAlreadyExistsError, ProductNotFoundError
from api.services.product import ProductService
from certifi import contents
from pydantic import BaseModel, Field
from fastapi import Body, Depends, FastAPI, HTTPException, Path, Query
from typing import Annotated, Literal
import json
import math

from config import MODE
from .schemas.product import ProductCreate, ProductDetail, ProductUpdate, ProductListResponse, ProductSummary, ProductBase
from .dependencies.filters import SortBy, ViewMode, NameMode, ProductsFilters, PaginationFilters
import aiosqlite
#python api\endpoints.py

@asynccontextmanager
async def lifespan(app: FastAPI):
  if MODE == 'TEST':
    await reset_db()
  else:
    await init_db()
  yield

app = FastAPI(lifespan=lifespan)

app.add_exception_handler(RepositoryError, repository_error_handler)
app.add_exception_handler(ProductNotFoundError, product_not_found_handler)
app.add_exception_handler(InvalidProductDataError, invalid_product_data_handler)
app.add_exception_handler(InvalidProductCategoryId, invalid_product_category_id_handler)
app.add_exception_handler(ProductAlreadyExistsError, product_already_exists_handler)

@app.get("/api/v1/products/{product_id}")
async def read_product(
    product_id : int, 
    product_service: Annotated[ProductRepository, Depends(get_product_service)]
) -> ProductDetail:
  result = await product_service.get(product_id)
  return result


@app.get("/api/v1/products", response_model=ProductListResponse)
async def read_products(pagination_filters : Annotated[PaginationFilters, Depends()], products_filters: Annotated[ProductsFilters, Depends()], produce_service: Annotated[ProductService, Depends(get_product_service)]):
  total, data = await produce_service.get_all(products_filters, pagination_filters) 
  return {
    "pagination" : {
      "page" : pagination_filters.page,
      "limit": pagination_filters.limit,
      "total" : total,
      "total_pages": math.ceil(total / pagination_filters.limit)
    },
    "data" : data
  }


@app.post('/api/v1/products', response_model=ProductDetail, status_code=201)
async def create_product(product : ProductCreate, product_service : Annotated[ProductService, Depends(get_product_service)]):
  product_created = await product_service.create(product)
  return product_created


@app.delete('/api/v1/products/{product_id}', status_code=204)
async def delete_product(product_id : int, product_service : Annotated[ProductService, Depends(get_product_service)]):
  await product_service.delete(product_id)

@app.patch('/api/v1/products/{product_id}', response_model=ProductDetail)
async def update_product(product_id: int, product: ProductUpdate, product_service: Annotated[ProductService, Depends(get_product_service)]):
  product_updated = await product_service.update(product_id, product)
  return product_updated
