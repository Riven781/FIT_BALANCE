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
from product_catalog_context.application.category_hierarchy_management_service import CategoryHierarchyManagementService
from product_catalog_context.application.product_issue_service import ProductIssueService
from product_catalog_context.application.product_management_service import ProductManagementService
from product_catalog_context.application.product_report_service import ProductReportService
from product_catalog_context.domain.category_hierarchy.product_category import ProductCategory
from product_catalog_context.domain.category_hierarchy.product_category_hierarchy import ProductCategoryHierarchy
from product_catalog_context.domain.category_hierarchy.product_category_hierarchy_status import ProductCategoryHierarchyStatus
from product_catalog_context.domain.users import CatalogManager, Moderator, ProductEditor
from product_catalog_context.infrastructure.adapters.access_adapter import AccessAdapter
from product_catalog_context.infrastructure.aiosqlite_repository.category_assignment_task_repository import CategoryAssignmentTaskRepository
from product_catalog_context.infrastructure.aiosqlite_repository.product import ProductRepository
from product_catalog_context.infrastructure.aiosqlite_repository.product_category_hierarchy import ProductCategoryHierarchyRepository
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from product_catalog_context.infrastructure.sql_alchemy_repository.mapper import mapper_registry
from sqlalchemy.event import listens_for

from product_catalog_context.domain.product.product import Product
from product_catalog_context.infrastructure.aiosqlite_repository.mapper import ProductMapper
from product_catalog_context.infrastructure.aiosqlite_repository.product_issue_repository import ProductIssueRepository
from product_catalog_context.infrastructure.aiosqlite_repository.product_report_repository import ProductReportRepository
from product_catalog_context.domain.enums.reported_field import ReportedField
from product_catalog_context.domain.issues.product_issue import ProductIssue
from product_catalog_context.domain.issues.product_issue_status import ProductIssueStatus
from product_catalog_context.domain.product.nutrition_facts import Nutrients, NutritionFacts, ReferenceQuantity
from product_catalog_context.domain.product.product import Product
from product_catalog_context.domain.product.product_assignment import CategoryAssignment
from product_catalog_context.domain.reports.product_report import ProductReport
from product_catalog_context.domain.reports.product_report_item import ProductReportItem
from product_catalog_context.domain.tasks.category_assignment_task import CategoryAssignmentTask
from product_catalog_context.domain.tasks.category_assignment_task_status import CategoryAssignmentTaskStatus
from product_catalog_context.infrastructure.sql_alchemy_repository.product import SqlAlchemyProductRepository
from product_catalog_context.infrastructure.sql_alchemy_repository.unit_of_work import SqlAlchemyUnitOfWork



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
"""
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
"""
"""
@pytest_asyncio.fixture
async def db_session(db_engine):
  SessionTest = async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)
  async with SessionTest() as session:
    yield session"""

@pytest_asyncio.fixture
async def db_engine():
  engine = create_async_engine(f'sqlite+aiosqlite:///:memory:')
  async with engine.begin() as conn:
    await conn.run_sync(mapper_registry.metadata.create_all)
  yield engine
  await engine.dispose()

@pytest_asyncio.fixture
async def db_session(db_engine):
  SessionTest = async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)
  @event.listens_for(db_engine.sync_engine, 'connect')
  def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute('PRAGMA foreign_keys=ON')
    cursor.close()
  async with SessionTest() as session:
    yield session


@pytest_asyncio.fixture
async def insert_data(db_session: AsyncSession):
  db_session.add(ProductCategoryHierarchy(hierarchy_id=1, status=ProductCategoryHierarchyStatus.ACTIVE, product_categories=[
    ProductCategory(
      category_id = 1,
      name = 'Produkty',
      parent_id=None
    ),
    ProductCategory(
      category_id=2,
      name = 'Roślinne',
      parent_id=1
    ),
    ProductCategory(
      category_id=3,
      name = 'Zwierzęce',
      parent_id=1
    ),
    ProductCategory(
      category_id=4,
      name = 'Schab',
      parent_id=3
    ),
    ProductCategory(
      category_id=5,
      name = 'Boczek',
      parent_id=3
    )
  ]))
  db_session.add(ProductCategoryHierarchy(hierarchy_id=2, status=ProductCategoryHierarchyStatus.PLANNED_FOR_PUBLICATION, product_categories=[
      ProductCategory(
        category_id = 6,
        name = 'Produkty',
        parent_id=None,
        source_node_id=1
      ),
      ProductCategory(
        category_id=7,
        name = 'Roślinnopodobne',
        parent_id=6,
        source_node_id=2
      ),
      ProductCategory(
        category_id=8,
        name = 'Zwierzęce',
        parent_id=6,
        source_node_id=3
      ),
      ProductCategory(
        category_id=9,
        name = 'Schabik',
        parent_id=8,
        source_node_id=4
      ),
      ProductCategory(
        category_id=10,
        name = 'Boczek',
        parent_id=8,
        source_node_id=5
      )
    ]))
  db_session.add(Product(product_id=1, name='Schab Drogi', brand_name='Auchan', nutrition_facts=NutritionFacts(kcal=300, reference_quantity=ReferenceQuantity(amount=100, unit='g'), nutrients=Nutrients(fat=100)), name_search_standard='schab drogi', category_assignments={1:CategoryAssignment(category_id=4), 2:CategoryAssignment(category_id=9)}))
  db_session.add(Product(product_id=2, name='Schab Tani', brand_name='Rambert', nutrition_facts=NutritionFacts(kcal=250, reference_quantity=ReferenceQuantity(amount=100, unit='g'), nutrients=Nutrients(fat=120)), name_search_standard='schab tani', category_assignments={1:CategoryAssignment(category_id=4)}))
  db_session.add(Product(product_id=3, name='Schab Średni', brand_name='XYZ', nutrition_facts=NutritionFacts(kcal=400, reference_quantity=ReferenceQuantity(amount=100, unit='g'), nutrients=Nutrients(fat=90)), name_search_standard='schab sredni', category_assignments={1:CategoryAssignment(category_id=4)}))
  db_session.add(Product(product_id=4, name='Tofu', brand_name='XYZ', nutrition_facts=NutritionFacts(kcal=300, reference_quantity=ReferenceQuantity(amount=100, unit='g'), nutrients=Nutrients(fat=40)), name_search_standard='tofu', category_assignments={1:CategoryAssignment(category_id=2)}))
  db_session.add(Product(product_id=5, name='Groszek', brand_name='ABC', nutrition_facts=NutritionFacts(kcal=100, reference_quantity=ReferenceQuantity(amount=100, unit='g'), nutrients=Nutrients(fat=100)), name_search_standard='groszek', category_assignments={1:CategoryAssignment(category_id=2)}))
  db_session.add(Product(product_id=6, name='Boczek Kaszubski', brand_name='WWW', nutrition_facts=NutritionFacts(kcal=500, reference_quantity=ReferenceQuantity(amount=100, unit='g'), nutrients=Nutrients(fat=100)), name_search_standard='boczek kaszubski', category_assignments={1:CategoryAssignment(category_id=5)}))
  db_session.add(Product(product_id=7, name='Boczek Cielęcy', brand_name='YYY', nutrition_facts=NutritionFacts(kcal=400, reference_quantity=ReferenceQuantity(amount=100, unit='g'), nutrients=Nutrients(fat=100)), name_search_standard='boczek cielecy', category_assignments={1:CategoryAssignment(category_id=5)}))
  db_session.add(Product(product_id=8, name='Raw Energy Baton kakaowy Bombus', brand_name='WWW', nutrition_facts=NutritionFacts(kcal=300, reference_quantity=ReferenceQuantity(amount=100, unit='g'), nutrients=Nutrients(fat=100)), name_search_standard='raw energy baton kakaowy bombus', category_assignments={1:CategoryAssignment(category_id=2)}))

  db_session.add(CategoryAssignmentTask(task_id=1, product_id=2, hierarchy_id=2, status=CategoryAssignmentTaskStatus.PENDING, user_id=1))
  db_session.add(CategoryAssignmentTask(task_id=2, product_id=2, hierarchy_id=1, status=CategoryAssignmentTaskStatus.PENDING, user_id=3))

  await db_session.flush()

  db_session.add(ProductIssue(issue_id=1, product_id=1, reported_field=ReportedField.KCAL, status=ProductIssueStatus.PENDING))
  db_session.add(ProductIssue(issue_id=2, product_id=1, reported_field=ReportedField.FAT, status=ProductIssueStatus.CONFIRMED, resolved_value=120))
  db_session.add(ProductIssue(issue_id=3, product_id=1, reported_field=ReportedField.SUGARS, status=ProductIssueStatus.PENDING))
  db_session.add(ProductIssue(issue_id=4, product_id=2, reported_field=ReportedField.FAT, status=ProductIssueStatus.REJECTED))

  db_session.add(ProductReport(report_id=1, product_id=1, reported_items=[
    ProductReportItem(reported_field=ReportedField.KCAL, proposed_value=120, issue_id=1),
    ProductReportItem(reported_field=ReportedField.FAT, issue_id=2)
    ], user_id=20))
  db_session.add(ProductReport(report_id=2, product_id=1, reported_items=[
    ProductReportItem(reported_field=ReportedField.KCAL, proposed_value=120, issue_id=1)
    ], user_id=10))

  await db_session.commit()
  await db_session.close()

@pytest_asyncio.fixture
async def insert_draft(db_session: AsyncSession):
  db_session.add(ProductCategoryHierarchy(hierarchy_id=3, status=ProductCategoryHierarchyStatus.DRAFT, product_categories=[
    ProductCategory(
      category_id = 11,
      name = 'Produkty',
      parent_id=None,
      source_node_id=1
    ),
    ProductCategory(
      category_id=12,
      name = 'Roślinnopodobne',
      parent_id=11,
      source_node_id=2
    ),
    ProductCategory(
      category_id=13,
      name = 'Zwierzęce',
      parent_id=11,
      source_node_id=3
    ),
    ProductCategory(
      category_id=14,
      name = 'Schabik',
      parent_id=13,
      source_node_id=4
    ),
    ProductCategory(
      category_id=15,
      name = 'Boczek',
      parent_id=13,
      source_node_id=5
    )
  ])) 
  await db_session.commit()
  await db_session.close()


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
def unit_of_work(db_session):
  return SqlAlchemyUnitOfWork(session=db_session)

class FakeAccessAdapter:
  def __init__(self, access_api: AccessApi):
    self.access_api = access_api

  async def get_product_editor_for(self, user_id):
    return ProductEditor(user_id)

  async def get_catalog_manager_for(self, user_id):
    return CatalogManager(user_id)

  async def get_moderator_for(self, user_id):
    return Moderator(user_id)

@pytest_asyncio.fixture
async def fake_access_adapter(access_api):
  return FakeAccessAdapter(access_api)

@pytest_asyncio.fixture
async def category_assignment_service(fake_access_adapter, unit_of_work) -> CategoryAssignmentTaskService:
  return CategoryAssignmentTaskService(unit_of_work=unit_of_work, access_adapter=fake_access_adapter)

@pytest_asyncio.fixture
async def category_hierarchy_management_service(unit_of_work, fake_access_adapter):
  return CategoryHierarchyManagementService(unit_of_work, fake_access_adapter)

@pytest_asyncio.fixture
async def alchemy_product_repository(db_session) -> CategoryAssignmentTaskService:
  return SqlAlchemyProductRepository(db_session)

@pytest_asyncio.fixture
async def product_management_service( unit_of_work, fake_access_adapter) -> ProductManagementService:
  return ProductManagementService(unit_of_work, fake_access_adapter)

@pytest_asyncio.fixture
async def product_repository(db) -> CategoryAssignmentTaskService:
  return ProductRepository(db)



@pytest_asyncio.fixture
async def product_report_service( unit_of_work, fake_access_adapter) -> ProductReportService:
  return ProductReportService(unit_of_work, fake_access_adapter)

@pytest_asyncio.fixture
async def product_issue_service(unit_of_work, fake_access_adapter) -> ProductReportService:
  return ProductIssueService(unit_of_work, fake_access_adapter)