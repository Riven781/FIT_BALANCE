from typing import Annotated

import aiosqlite
from fastapi import Depends

from identity_and_access_context.public.adapters.fastapi.dependencies.get_identity_api import get_identity_api
from identity_and_access_context.public.api.access_api import AccessApi
from identity_and_access_context.public.adapters.fastapi.dependencies.get_access_api import get_access_api
from identity_and_access_context.public.api.identity_api import IdentityApi
from product_catalog_context.application.category_assignment_task_service import CategoryAssignmentTaskService
from product_catalog_context.application.product_management_service import ProductManagementService
from product_catalog_context.application.product_query_service import ProductQueryService
from product_catalog_context.application.product_report_service import ProductReportService
from product_catalog_context.application.unit_of_work import UnitOfWork
from product_catalog_context.domain.messages.domain_message_publisher import DomainMessagePublisher
from product_catalog_context.infrastructure.adapters.access_adapter import AccessAdapter
from product_catalog_context.infrastructure.adapters.identity_adapter import IdentityAdapter
from product_catalog_context.infrastructure.aiosqlite_queries.product import ProductQueries
from product_catalog_context.infrastructure.outbox.subscriber import OutboxSubscriber
from product_catalog_context.infrastructure.sql_alchemy_repository.unit_of_work import SqlAlchemyUnitOfWork
from shared.database.db import get_db
from product_catalog_context.infrastructure.aiosqlite_repository.product import ProductRepository
from product_catalog_context.infrastructure.aiosqlite_repository.product_category_hierarchy import ProductCategoryHierarchyRepository
from product_catalog_context.application.category_hierarchy_management_service import CategoryHierarchyManagementService
from shared.database.session import get_session, get_sqlalchemy_session_factory
from shared.infrastructure.fastapi.security.contracts import RawAuthenticationCredentials
from shared.infrastructure.fastapi.security.dependencies import get_raw_authentication_credentials
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

async def get_access_adapter(access_api: Annotated[AccessApi, Depends(get_access_api)]):
  return AccessAdapter(access_api)

async def get_identity_adapter(identity_api: Annotated[IdentityApi, Depends(get_identity_api)]):
  return IdentityAdapter(identity_api)

#it should be used in many routes
async def get_current_user_id(identity_adapter: Annotated[IdentityAdapter, Depends(get_identity_adapter)], credentials: Annotated[RawAuthenticationCredentials, Depends(get_raw_authentication_credentials)]):
  return await identity_adapter.get_current_user_id(credentials) #identity adapter can use rest in future

async def get_product_repository(db: Annotated[aiosqlite.Connection, Depends(get_db)]):
  return ProductRepository(db)

async def get_product_queries(db: Annotated[aiosqlite.Connection, Depends(get_db)]):
  return ProductQueries(db)



async def get_product_query_service(product_queries: Annotated[ProductQueries, Depends(get_product_queries)]):
  return ProductQueryService(product_queries)

async def get_product_category_hierarchy_repository(db: Annotated[aiosqlite.Connection, Depends(get_db)]):
  return ProductCategoryHierarchyRepository(db)

async def get_message_publisher(): #it could be global
  subscriber = OutboxSubscriber()
  publisher = DomainMessagePublisher()
  publisher.global_subscribe(subscriber)
  return publisher

def get_session_factory():
  return get_sqlalchemy_session_factory()


async def get_unit_of_work(session_factory: Annotated[async_sessionmaker[AsyncSession], Depends(get_session_factory)]): #it could be global
  return SqlAlchemyUnitOfWork(session_factory=session_factory)


async def get_product_management_service(
    unit_of_work: Annotated[UnitOfWork, Depends(get_unit_of_work)], 
    access_adapter: Annotated[AccessAdapter, Depends(get_access_adapter)],
    publisher: Annotated[DomainMessagePublisher, Depends(get_message_publisher)]):
  return ProductManagementService(unit_of_work, access_adapter, publisher)

async def get_product_hierarchy_category_service(
    unit_of_work: Annotated[UnitOfWork, Depends(get_unit_of_work)], 
    access_adapter: Annotated[AccessAdapter, Depends(get_access_adapter)],
    publisher: Annotated[DomainMessagePublisher, Depends(get_message_publisher)]):
  return CategoryHierarchyManagementService(unit_of_work, access_adapter, publisher)

async def get_category_assignment_task_service(
    unit_of_work: Annotated[UnitOfWork, Depends(get_unit_of_work)], 
    access_adapter: Annotated[AccessAdapter, Depends(get_access_adapter)]):
  return CategoryAssignmentTaskService(unit_of_work, access_adapter)

def get_product_report_service(
  unit_of_work: Annotated[UnitOfWork, Depends(get_unit_of_work)], 
  access_adapter: Annotated[AccessAdapter, Depends(get_access_adapter)],
  publisher: Annotated[DomainMessagePublisher, Depends(get_message_publisher)]
):
  return ProductReportService(unit_of_work, access_adapter, publisher)