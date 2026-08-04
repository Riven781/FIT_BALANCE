from typing import Annotated

import aiosqlite
from fastapi import Depends

from shared.database.db import get_db
from product_catalog_context.infrastructure.aiosqlite_repository.product import ProductRepository
from product_catalog_context.infrastructure.aiosqlite_repository.product_category import ProductCategoryRepository
from product_catalog_context.infrastructure.aiosqlite_repository.product_category_hierarchy import ProductCategoryHierarchyRepository
from product_catalog_context.application.product import ProductService
from product_catalog_context.application.product_category import ProductCategoryService


async def get_product_repository(db: Annotated[aiosqlite.Connection, Depends(get_db)]):
  return ProductRepository(db)

async def get_product_service(product_repository: Annotated[ProductRepository, Depends(get_product_repository)]):
  return ProductService(product_repository)

async def get_product_category_repository(db: Annotated[aiosqlite.Connection, Depends(get_db)]):
  return ProductCategoryRepository(db)

async def get_product_category_hierarchy_repository(db: Annotated[aiosqlite.Connection, Depends(get_db)]):
  return ProductCategoryHierarchyRepository(db)


async def get_product_category_service(
    product_category_repository: Annotated[ProductCategoryRepository, Depends(get_product_category_repository)],
    product_category_hierarchy_repository: Annotated[ProductCategoryHierarchyRepository, Depends(get_product_category_hierarchy_repository)]):
  return ProductCategoryService(product_category_repository, product_category_hierarchy_repository)