from fastapi import APIRouter
from fastapi import Depends
from typing import Annotated
from product_catalog_context.infrastructure.aiosqlite_repository.product import ProductRepository
from product_catalog_context.application.product_category import ProductCategoryService
from config import MODE
from product_catalog_context.infrastructure.api.rest.schemas.product import ProductCreate, ProductDetail, ProductUpdate, ProductListResponse
from product_catalog_context.infrastructure.api.rest.schemas.product_category import ProductCategory, ProductCategoryHierarchy
import math
from product_catalog_context.infrastructure.api.rest.dependencies.database import get_product_category_service, get_product_repository, get_product_service
from product_catalog_context.application.product import ProductService
from product_catalog_context.infrastructure.api.rest.dependencies.filters import SortBy, NameMode, ProductsFilters, PaginationFilters


product_catalog_router = APIRouter()

@product_catalog_router.get("/api/v1/products/{product_id}")
async def read_product(
    product_id : int, 
    product_service: Annotated[ProductRepository, Depends(get_product_service)]
) -> ProductDetail:
  result = await product_service.get(product_id)
  return result


@product_catalog_router.get("/api/v1/products", response_model=ProductListResponse)
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

@product_catalog_router.post('/api/v1/products', response_model=ProductDetail, status_code=201)
async def create_product(product : ProductCreate, product_service : Annotated[ProductService, Depends(get_product_service)]):
  product_created = await product_service.create(product)
  return product_created


@product_catalog_router.delete('/api/v1/products/{product_id}', status_code=204)
async def delete_product(product_id : int, product_service : Annotated[ProductService, Depends(get_product_service)]):
  await product_service.delete(product_id)

@product_catalog_router.patch('/api/v1/products/{product_id}', response_model=ProductDetail)
async def update_product(product_id: int, product: ProductUpdate, product_service: Annotated[ProductService, Depends(get_product_service)]):
  product_updated = await product_service.update(product_id, product)
  return product_updated


@product_catalog_router.get('api/v1/product-categories/hierarchy', response_model=list[ProductCategoryHierarchy])
async def read_category_hierarchy(product_category_service: Annotated[ProductCategoryService, Depends(get_product_category_service)]):
  return await product_category_service.get_hierarchy()

@product_catalog_router.put('api/v1/product-categories/hierarchy', response_model=list[ProductCategoryHierarchy])
async def update_category_hierarchy(product_categories: list[ProductCategory], product_category_service: Annotated[ProductCategoryService, Depends(get_product_category_service)]):
  return await product_category_service.update_hierarchy(product_categories)

@product_catalog_router.get('api/v1/product-categories', response_model=list[ProductCategory])
async def read_categories(product_category_service: Annotated[ProductCategoryService, Depends(get_product_category_service)]):
  return await product_category_service.get_all()

