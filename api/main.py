from enum import Enum
from os import name
import re
from unittest import result
import aiofiles
import asyncio
from fastapi.encoders import jsonable_encoder
from api.dependencies.database import get_product_repository, get_product_service
from api.dependencies.product import check_ids
from api.repository.aiosqlite.product import ProductRepository
from api.services.product import ProductService
from certifi import contents
from pydantic import BaseModel, Field
from fastapi import Body, Depends, FastAPI, HTTPException, Path, Query
from typing import Annotated, Literal
import json
import math
from .schemas.product import ProductCreate, ProductDetail, ProductUpdate, ProductListResponse, ProductSummary, ProductBase
from .dependencies.filters import SortBy, ViewMode, NameMode, ProductsFilters, PaginationFilters
import aiosqlite
#python api\endpoints.py


app = FastAPI()


@app.get("/api/v1/products/{product_id}")
async def read_product(
    product_id : int, 
    product_repo: Annotated[ProductRepository, Depends(get_product_repository)]
) -> ProductDetail:
  result = await product_repo.get_by_id(product_id)
  if result is None:
    raise HTTPException(status_code=404, detail='Not Found')
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


@app.post('/api/v1/products', response_model=ProductDetail)
async def create_product(product : ProductCreate, product_service : Annotated[ProductService, Depends(get_product_service)]):
  try:
    product_created = await product_service.create(product)
    return product_created
  except aiosqlite.Error as e:
    #print(e)
    raise HTTPException(500, detail="Database error")
  except HTTPException:
    raise
  except Exception as e:
    #print(e)
    raise HTTPException(500)

@app.delete('/api/v1/products/{product_id}')
async def delete_product(product_id : int, product_service : Annotated[ProductService, Depends(get_product_service)]):
  await product_service.delete(product_id)

@app.patch('/api/v1/products/{product_id}', response_model=ProductDetail, dependencies=[Depends(check_ids)])
async def update_product(product_id: int, product: ProductUpdate, product_service: Annotated[ProductService, Depends(get_product_service)]):
  try:
    product_updated = await product_service.update(product_id, product)
    return product_updated
  except aiosqlite.Error as e:
    raise HTTPException(500, detail="Databse error")
  except HTTPException:
    raise
  except Exception as e:
    print(e)
    raise HTTPException(500)




