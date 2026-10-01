from fastapi import APIRouter
from fastapi import Depends
from typing import Annotated
from product_catalog_context.application.product_management_service import ProductManagementService
from product_catalog_context.infrastructure.aiosqlite_repository.product import ProductRepository
from config import MODE
from product_catalog_context.infrastructure.api.rest.schemas.product import ProductPostRequest, ProductPutRequest, ProductResponse, PublicProductListResponse, PublicProductResponse
from product_catalog_context.infrastructure.api.rest.schemas.product_category import ProductCategory, ProductCategoryHierarchy
import math
from product_catalog_context.infrastructure.api.rest.dependencies.database import get_current_user_id, get_product_management_service, get_product_query_service, get_product_repository
from product_catalog_context.application.product_query_service import ProductQueryService
from product_catalog_context.infrastructure.api.rest.dependencies.filters import SortBy, NameMode, ProductsFilters, PaginationFilters
from product_catalog_context.application.category_hierarchy_management_service import CategoryHierarchyManagementService

product_router = APIRouter()

@product_router.get("/api/v1/products/{product_id}")
async def read_product_detail(
    product_id : int, 
    product_query_service: Annotated[ProductQueryService, Depends(get_product_query_service)]
) -> PublicProductResponse:
  result = await product_query_service.get(product_id)
  return result

@product_router.get("/api/v1/products", response_model=PublicProductListResponse)
async def read_products(
  pagination_filters : Annotated[PaginationFilters, Depends()],
  products_filters: Annotated[ProductsFilters, Depends()],
  product_query_service: Annotated[ProductQueryService, Depends(get_product_query_service)]
):
  total, data = await product_query_service.get_all(products_filters.to_command(), pagination_filters.to_command())
  return {
    "pagination" : {
      "page" : pagination_filters.page,
      "limit": pagination_filters.limit,
      "total" : total,
      "total_pages": math.ceil(total / pagination_filters.limit)
    },
    "data" : data
  }

@product_router.post('/api/v1/products', response_model=ProductResponse, status_code=201)
async def create_product(
  product : ProductPostRequest, 
  product_management_service : Annotated[ProductManagementService, Depends(get_product_management_service)],
  user_id : Annotated[int, Depends(get_current_user_id)]
):
  product_created = await product_management_service.create(product.to_command(), product_editor_id=user_id)
  return product_created


@product_router.delete('/api/v1/products/{product_id}', status_code=204)
async def delete_product(
  product_id : int, 
  product_management_service : Annotated[ProductManagementService, Depends(get_product_management_service)],
  user_id : Annotated[int, Depends(get_current_user_id)]
):
  await product_management_service.delete(product_id, product_editor_id=user_id)

@product_router.put('/api/v1/products/{product_id}', response_model=ProductResponse)
async def update_product(
  product_id: int, product: ProductPutRequest, 
  product_management_service: Annotated[ProductManagementService, Depends(get_product_management_service)],
  user_id : Annotated[int, Depends(get_current_user_id)]
):
  product_updated = await product_management_service.update(product_id, product.to_command(), product_editor_id=user_id)
  return product_updated
