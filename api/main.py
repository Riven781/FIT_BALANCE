from enum import Enum
from os import name
import re
from unittest import result

from fastapi.encoders import jsonable_encoder
from api.dependencies.product import check_ids
from api.services.product import get_products
from pydantic import BaseModel, Field
from fastapi import Body, Depends, FastAPI, HTTPException, Path, Query
from typing import Annotated, Literal
import json
import math
from .schemas.product import ProductDetail, ProductDetailUpdate, ProductListResponse, ProductSummary, ProductBase
from .dependencies.filters import SortBy, ViewMode, NameMode, ProductsFilters, PaginationFilters
#python api\endpoints.py

with open('./api/products.json', encoding='utf-8') as products_file:
  products = json.load(products_file)
  product_by_id = {product['id'] : product for product in products}

with open('./api/products_hierarchy_2.json', encoding='utf-8') as products_hierarchy_file:
  products_hierarchy = json.load(products_hierarchy_file)


app = FastAPI()

@app.get("/api/v1/")
async def root():
  return {"message" : "Hello World!"}


@app.get("/api/v1/product/{product_id}")
async def read_product(product_id : int) -> ProductDetail | None:
  return product_by_id.get(product_id)


@app.get("/api/v1/products", response_model=ProductListResponse)
async def read_products(pagination_filters : Annotated[PaginationFilters, Depends()], products_filters: Annotated[ProductsFilters, Depends()]):
  start_index = (pagination_filters.page - 1) * pagination_filters.limit
  data = get_products(products_filters, product_by_id, products_hierarchy)
  return {
    "pagination" : {
      "page" : pagination_filters.page,
      "limit": pagination_filters.limit,
      "total" : len(data),
      "total_pages": math.ceil(len(data) / pagination_filters.limit)
    },
    "data" : data[start_index : start_index + pagination_filters.limit]
  }


@app.patch('/api/v1/product/{product_id}', dependencies=[Depends(check_ids)])
async def update_product(product_id: Annotated[int, Path(title='The id of the product to get')], product: ProductDetailUpdate):
  stored_product_data = product_by_id.get(product_id)
  if stored_product_data is None:
    raise HTTPException(status_code=404, detail="Product not found")
  stored_product_model = ProductDetail(**stored_product_data)
  update_data = product.model_dump(exclude_unset=True)
  updated_product = stored_product_model.model_copy(update=update_data)

  product_by_id[product_id].update(jsonable_encoder(updated_product)) 

  return updated_product

