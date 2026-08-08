from typing import Annotated

import aiosqlite
from fastapi import Depends

from product_catalog_context.application.product_management_service import ProductManagementService
from product_catalog_context.application.product_query_service import ProductQueryService
from product_catalog_context.infrastructure.aiosqlite_queries.product import ProductQueries
from shared.database.db import get_db
from product_catalog_context.infrastructure.aiosqlite_repository.product import ProductRepository
from product_catalog_context.infrastructure.aiosqlite_repository.product_category import ProductCategoryRepository
from product_catalog_context.infrastructure.aiosqlite_repository.product_category_hierarchy import ProductCategoryHierarchyRepository
from product_catalog_context.application.product_category import ProductCategoryService


async def get_product_repository(db: Annotated[aiosqlite.Connection, Depends(get_db)]):
  return ProductRepository(db)

async def get_product_queries(db: Annotated[aiosqlite.Connection, Depends(get_db)]):
  return ProductQueries(db)

async def get_product_management_service(product_repository: Annotated[ProductRepository, Depends(get_product_repository)]):
  return ProductManagementService(product_repository)

async def get_product_query_service(product_queries: Annotated[ProductQueries, Depends(get_product_queries)]):
  return ProductQueryService(product_queries)

async def get_product_category_repository(db: Annotated[aiosqlite.Connection, Depends(get_db)]):
  return ProductCategoryRepository(db)

async def get_product_category_hierarchy_repository(db: Annotated[aiosqlite.Connection, Depends(get_db)]):
  return ProductCategoryHierarchyRepository(db)


async def get_product_category_service(
    product_category_repository: Annotated[ProductCategoryRepository, Depends(get_product_category_repository)],
    product_category_hierarchy_repository: Annotated[ProductCategoryHierarchyRepository, Depends(get_product_category_hierarchy_repository)]):
  return ProductCategoryService(product_category_repository, product_category_hierarchy_repository)