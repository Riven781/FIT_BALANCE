from typing import Annotated

import aiosqlite
from fastapi import Depends

from identity_and_access_context.public.adapters.fastapi.dependencies.get_identity_api import get_identity_api
from identity_and_access_context.public.api.access_api import AccessApi
from identity_and_access_context.public.adapters.fastapi.dependencies.get_access_api import get_access_api
from identity_and_access_context.public.api.identity_api import IdentityApi
from product_catalog_context.application.product_management_service import ProductManagementService
from product_catalog_context.application.product_query_service import ProductQueryService
from product_catalog_context.infrastructure.adapters.access_adapter import AccessAdapter
from product_catalog_context.infrastructure.adapters.identity_adapter import IdentityAdapter
from product_catalog_context.infrastructure.aiosqlite_queries.product import ProductQueries
from shared.database.db import get_db
from product_catalog_context.infrastructure.aiosqlite_repository.product import ProductRepository
from product_catalog_context.infrastructure.aiosqlite_repository.product_category import ProductCategoryRepository
from product_catalog_context.infrastructure.aiosqlite_repository.product_category_hierarchy import ProductCategoryHierarchyRepository
from product_catalog_context.application.category_hierarchy_management_service import ProductCategoryService
from shared.infrastructure.fastapi.security.contracts import RawAuthenticationCredentials
from shared.infrastructure.fastapi.security.dependencies import get_raw_authentication_credentials

async def get_access_adapter(access_api: Annotated[AccessApi, Depends(get_access_api)]):
  return AccessAdapter(access_api)

async def get_identity_adapter(identity_api: Annotated[IdentityApi, Depends(get_identity_api)]):
  return IdentityAdapter(identity_api)

#it should be used in many routes
async def get_current_user_id(identity_adapter: Annotated[IdentityApi, Depends(get_identity_adapter)], credentials: Annotated[RawAuthenticationCredentials, Depends(get_raw_authentication_credentials)]):
  return await identity_adapter.get_current_user(credentials) #identity adapter can use rest in future

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