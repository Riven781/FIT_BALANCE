from abc import ABC, abstractmethod
from dataclasses import asdict
import re

from sqlalchemy import StaticPool, text
from sqlalchemy import event
from identity_and_access_context.application.access_service import AccessService
from identity_and_access_context.infrastructure.sql_alchemy_repository.user_repository import SqlAlchemyUserRepository
from identity_and_access_context.infrastructure.sql_alchemy_repository.user_roles_repository import SqlAlchemyUserRolesRepository
from identity_and_access_context.public.adapters.fastapi.dependencies.get_access_api import get_access_api
from identity_and_access_context.public.api.access_api import AccessApi
from product_catalog_context.application.category_assignment_task_service import CategoryAssignmentTaskService
from product_catalog_context.application.product_issue_service import ProductIssueService
from product_catalog_context.application.product_management_service import ProductManagementService
from product_catalog_context.application.product_report_service import ProductReportService
from product_catalog_context.domain.category_hierarchy.product_category import ProductCategory
from product_catalog_context.domain.category_hierarchy.product_category_hierarchy import ProductCategoryHierarchy
from product_catalog_context.infrastructure.adapters.access_adapter import AccessAdapter
from product_catalog_context.infrastructure.aiosqlite_repository.category_assignment_task_repository import CategoryAssignmentTaskRepository
from product_catalog_context.infrastructure.aiosqlite_repository.product import ProductRepository
from product_catalog_context.infrastructure.aiosqlite_repository.product_category_hierarchy import ProductCategoryHierarchyRepository
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from identity_and_access_context.infrastructure.sql_alchemy_repository.mapper import mapper_registry
from sqlalchemy.event import listens_for

from product_catalog_context.domain.product.product import Product
from product_catalog_context.infrastructure.aiosqlite_repository.mapper import ProductMapper
from product_catalog_context.infrastructure.aiosqlite_repository.product_issue_repository import ProductIssueRepository
from product_catalog_context.infrastructure.aiosqlite_repository.product_report_repository import ProductReportRepository




@pytest_asyncio.fixture
async def fake_product_repository():
  class FakeProductRepository():
    def __init__(self, product_list):
      self.products = product_list
    async def get_by_id(self, id):
      return next((product for product in self.products if product.product_id == id), None)
    
    
    async def insert(self, product):
      self.products.append(product)
      return product.product_id
    
    async def update(self, id, updated_product : Product):
      count = 0
      for i, product in enumerate(self.products):
        if id == product.product_id:
          self.products[i] = updated_product
          count += 1
      return count
    
    async def delete(self, id):
      count = 0
      for i, product in enumerate(self.products):
        if id == product.product_id:
          self.products.pop(i)
          count += 1
          break
      return count

      
    async def commit(self):
      pass

  return FakeProductRepository


@pytest_asyncio.fixture
async def fake_product_queries():
  class FakeProductQueries:
    def __init__(self, product_list):
        self.products = product_list


    async def get_detail_by_id(self, id):
      return next((product for product in self.products if product.product_id == id), None)

    async def get_detail_by_filters(self, **filters):
      results = list(self.products)
      if filters.get('category_id'):
        results = [product for product in results if filters.get('category_id') in product.category_assignments.values()]
        print(results)
      if names := filters.get('names'):
        after_space = [f' {name}' for name in names]
        at_the_begining = [f'^{name}' for name in names]
        re_statement = [f"{option1}|{option2}" for option1, option2 in zip(after_space, at_the_begining)] 
        print(re_statement)
        for product in results[:]:
          is_found = all(re.search(rs, product.name_search_standard) for rs in re_statement)
          if not is_found:
            results.remove(product)
      return results

    async def get_total(self, **filters):
      return len(await self.get_detail_by_filters(**filters))

  return FakeProductQueries


import pytest
import aiosqlite
from sqlalchemy.engine import Engine
from shared.database.create_new_db import product_table_query, product_category_node_table_query, product_category_hierarchy_query, product_category_assignment, product_category_closure_query, product_category_assignment_task
from shared.database.create_new_db import fields, report, report_item, issue, user, role, user_role, id_sequence, init_id_seq, user_roles



@pytest_asyncio.fixture
async def hierarchy_repository(db):
  repo = ProductCategoryHierarchyRepository(db)
  category_1 = ProductCategory(name='Batony', category_id=10, parent_id=None)
  category_2 = ProductCategory(name='Batony proteinowe', category_id=11, parent_id=None)

  await repo.insert(ProductCategoryHierarchy(status='ACTIVE', product_categories=[category_1, category_2]))
  return ProductCategoryHierarchyRepository(db)

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
  cursor = dbapi_connection.cursor()
  cursor.execute("PRAGMA foreign_keys=ON")
  cursor.close()

@pytest_asyncio.fixture
async def db_engine():
  engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    poolclass=StaticPool,
  )

    # Inicjalizacja schematu bazy danych na TYM SAMYM połączeniu
  async with engine.begin() as conn:
    # PRAGMA foreign_keys w SQLite musimy włączyć ręcznie dla każdego połączenia
    await conn.execute(text("PRAGMA foreign_keys = ON"))
    queries = [
      product_table_query,
      product_category_node_table_query,
      product_category_hierarchy_query,
      product_category_assignment,
      product_category_closure_query,
      product_category_assignment_task,
      fields,
      report,
      report_item,
      issue,
      user,
      role,
      user_role,
      user_roles,
      id_sequence,
      init_id_seq,
    ]
        
    for q in queries:
      await conn.execute(text(q))

  yield engine

  await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine):
  SessionTest = async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)
  async with SessionTest() as session:
    yield session


# Opcjonalnie: jeśli nadal potrzebujesz bezpośredniego dostępu do surowego aiosqlite connection
@pytest_asyncio.fixture
async def db(db_engine):
  async with db_engine.connect() as conn:
    raw_db = await conn.get_raw_connection()
    driver_conn = raw_db.driver_connection  # Obiekt aiosqlite.Connection
    # Ustawiamy row_factory, aby zapytań można było używać jak słowników
    driver_conn.row_factory = aiosqlite.Row
    yield raw_db.driver_connection

@pytest_asyncio.fixture
async def user_roles_repository(db_session):
  return SqlAlchemyUserRolesRepository(db_session)

@pytest_asyncio.fixture
async def access_service(user_roles_repository):
  return AccessService(user_roles_repository)

@pytest_asyncio.fixture
async def access_api(access_service):
  return AccessApi(access_service)

@pytest_asyncio.fixture
async def access_adapter(access_api):
  return AccessAdapter(access_api)


@pytest_asyncio.fixture
async def category_assignment_service(db, access_adapter) -> CategoryAssignmentTaskService:
  hierarchy_repo = ProductCategoryHierarchyRepository(db)
  product_repo = ProductRepository(db)
  task_repo = CategoryAssignmentTaskRepository(db)

  return CategoryAssignmentTaskService(category_assignment_task_repository=task_repo, product_category_hierarchy_repository=hierarchy_repo, product_repository=product_repo, access_adapter=access_adapter)

@pytest_asyncio.fixture
async def product_management_service(db, access_adapter) -> CategoryAssignmentTaskService:
  hierarchy_repo = ProductCategoryHierarchyRepository(db)
  product_repo = ProductRepository(db)
  return ProductManagementService(product_repository=product_repo, product_category_hierarchy_repository=hierarchy_repo, access_adapter=access_adapter)

@pytest_asyncio.fixture
async def product_repository(db) -> CategoryAssignmentTaskService:
  return ProductRepository(db)



@pytest_asyncio.fixture
async def product_report_service(db, access_adapter) -> ProductReportService:
  async with db.executescript(
    """  
    INSERT INTO User(id, username, email, hashed_password) VALUES 
      (1, 'ZYZ','xyz@gm.c','xyz');

    INSERT INTO Product (id, name, brand_name, kcal, reference_amount, reference_unit, name_search_standard)
    VALUES 
    (1, "Schab Drogi", "Auchan", 300, 100, "g","schab drogi");
    
    INSERT INTO ProductIssue (id, product_id, status, reported_field)
    VALUES
    (99, 1, 'rejected', 'sugars'),
    (100, 1, 'pending', 'sugars')
    
    """
  ) as cursor:
    pass
  report_repo = ProductReportRepository(db)
  issue_repo = ProductIssueRepository(db)
  return ProductReportService(report_repo, issue_repo, access_adapter)

@pytest_asyncio.fixture
async def product_issue_service(db, access_adapter) -> ProductReportService:
  async with db.executescript(
    """
    INSERT INTO User(id, username, email, hashed_password) VALUES 
      (1, 'ZYZ','xyz@gm.c','xyz'), 
      (2, 'ABC','abc@gm.c','abc');
    
    INSERT INTO UserRoles(user_id, version) VALUES 
      (1, 1), 
      (2, 1);
    
    INSERT INTO UserRole(user_id, role) VALUES 
      (1, 'moderator'),
      (1, 'catalog_manager'),
      (2, 'product_editor');

    INSERT INTO Product (id, name, brand_name, kcal, reference_amount, reference_unit, name_search_standard)
    VALUES 
    (1, "Schab Drogi", "Auchan", 300, 100, "g","schab drogi");
    
    INSERT INTO ProductIssue (id, product_id, status, reported_field)
    VALUES
    (99, 1, 'rejected', 'sugars'),
    (100, 1, 'pending', 'sugars'),
    (101, 1, 'pending', 'fat'),(102, 1, 'confirmed', 'fat');
    
    """
  ) as cursor:
    pass
  issue_repo = ProductIssueRepository(db)
  return ProductIssueService(issue_repo, access_adapter)