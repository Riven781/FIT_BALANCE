import asyncio
from pathlib import Path
import subprocess
import sys

from identity_and_access_context.application.access_service import AccessService
from identity_and_access_context.infrastructure.sql_alchemy_repository.user_roles_repository import SqlAlchemyUserRolesRepository
from identity_and_access_context.public.api.access_api import AccessApi
from product_catalog_context.application.category_hierarchy_management_service import CategoryHierarchyManagementService
from product_catalog_context.application.handlers.delete_category_assignment_tasks import DeleteCategoryAssignmentTasks
from product_catalog_context.application.product_issue_service import ProductIssueService
from product_catalog_context.application.product_management_service import ProductManagementService
from product_catalog_context.application.product_report_service import ProductReportService
from product_catalog_context.application.unit_of_work import UnitOfWork
from product_catalog_context.domain.category_hierarchy.events import  HierarchyRevertedToDraft
from product_catalog_context.domain.enums.reported_field import ReportedField
from product_catalog_context.domain.issues.product_issue import ProductIssue
from product_catalog_context.domain.issues.product_issue_status import ProductIssueStatus
from product_catalog_context.domain.messages.domain_message_publisher import DomainMessagePublisher
from product_catalog_context.domain.messages.event_bus import EventBus
from product_catalog_context.domain.messages.message_registry import MessageRegistry
from product_catalog_context.domain.messages.message_serializer import MessageSerializer
from product_catalog_context.domain.reports.product_report import ProductReport
from product_catalog_context.domain.reports.product_report_item import ProductReportItem
from product_catalog_context.domain.users import CatalogManager, Moderator, ProductEditor
from product_catalog_context.infrastructure.outbox.event_dispatcher import OutboxEventDispatcher
from product_catalog_context.infrastructure.outbox.repository import OutboxDAO
from product_catalog_context.infrastructure.outbox.subscriber import DoubleOutboxSubscriber, OutboxSubscriber
from product_catalog_context.infrastructure.sql_alchemy_repository.mapper import mapper_registry
from product_catalog_context.infrastructure.outbox.mapper import outbox_mapper_registry
from product_catalog_context.domain.category_hierarchy.product_category_hierarchy import ProductCategoryHierarchy
from product_catalog_context.domain.category_hierarchy.product_category import ProductCategory
from product_catalog_context.domain.category_hierarchy.product_category_hierarchy_status import ProductCategoryHierarchyStatus
from product_catalog_context.domain.product.product import Product
from product_catalog_context.domain.product.nutrition_facts import Nutrients, NutritionFacts, ReferenceQuantity
from product_catalog_context.domain.product.product_assignment import CategoryAssignment
from product_catalog_context.domain.tasks.category_assignment_task import CategoryAssignmentTask
from product_catalog_context.domain.tasks.category_assignment_task_status import CategoryAssignmentTaskStatus
from product_catalog_context.infrastructure.sql_alchemy_repository.category_assignment_task import SqlAlchemyCategoryAssignmentTaskRepository

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import event
import pytest_asyncio
from sqlalchemy.pool import StaticPool

from product_catalog_context.infrastructure.sql_alchemy_repository.plan_hierarchy_for_publication_saga_repository import SqlAlchemyPlanHierarchyForPublicationSagaRepository
from product_catalog_context.infrastructure.sql_alchemy_repository.product import SqlAlchemyProductRepository
from product_catalog_context.infrastructure.sql_alchemy_repository.product_issue import SqlAlchemyProductIssueRepository
from product_catalog_context.infrastructure.sql_alchemy_repository.product_issue_confirmation_saga_repository import SqlAlchemyProductIssueConfirmationSagaRepository
from product_catalog_context.infrastructure.sql_alchemy_repository.unit_of_work import SqlAlchemyUnitOfWork, SqlAlchemyUnitOfWorkFactory

@pytest_asyncio.fixture
def db_path(tmp_path):
    return (tmp_path / "test.db").resolve()


@pytest_asyncio.fixture
def database_url(db_path):
    return f"sqlite+aiosqlite:///{db_path.as_posix()}"


@pytest_asyncio.fixture
async def event_outbox_dispatcher(db_path):
  process = await asyncio.create_subprocess_exec(
    sys.executable, 
    '-m', 
    'product_catalog_context.infrastructure.outbox.event_dispatcher', 
    '--database-url', 
    db_path,
    creationflags=subprocess.CREATE_NEW_CONSOLE)
  yield process
  #await asyncio.sleep(10)
  if process.returncode is None:
    process.terminate()
    await process.wait()



@pytest_asyncio.fixture
async def start_event_dispatcher():
  processes = []

  async def start(db_path, double_messages=False):
    args = [
      sys.executable,
      "-m",
      "product_catalog_context.infrastructure.outbox.event_dispatcher",
      "--database-url",
      db_path,
    ]
    if double_messages:
      args.append('--double-message')
    process = await asyncio.create_subprocess_exec(
       *args,
        creationflags=subprocess.CREATE_NEW_CONSOLE,
    )

    processes.append(process)
    return process

  yield start

  for process in processes:
    if process.returncode is None:
      process.terminate()
      await process.wait()

@pytest_asyncio.fixture
async def start_command_dispatcher():
  processes = []
  

  async def start(db_path, double_messages=False):
    args = [
      sys.executable,
      "-m",
      "product_catalog_context.infrastructure.outbox.command_dispatcher",
      "--database-url",
      db_path,
    ]
    if double_messages:
      args.append('--double-message')
    process = await asyncio.create_subprocess_exec(
      *args,
      creationflags=subprocess.CREATE_NEW_CONSOLE,
    )
   
    processes.append(process)
    return process

  yield start

  for process in processes:
    if process.returncode is None:
      process.terminate()
      await process.wait()



@pytest_asyncio.fixture
async def command_outbox_dispatcher(db_path):
  process = await asyncio.create_subprocess_exec(
    sys.executable, 
    '-m', 
    'product_catalog_context.infrastructure.outbox.command_dispatcher', 
    '--database-url', 
    db_path,
    creationflags=subprocess.CREATE_NEW_CONSOLE)
  yield process
  #await asyncio.sleep(10)
  if process.returncode is None:
    process.terminate()
    await process.wait()

@pytest_asyncio.fixture
async def engine(db_path):

  engine = create_async_engine(f'sqlite+aiosqlite:///{db_path}')
  return engine

@pytest_asyncio.fixture
async def session_factory(engine):
  session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
  return session_factory
  
@pytest_asyncio.fixture
async def db_session(engine, session_factory):
  @event.listens_for(engine.sync_engine, 'connect')
  def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute('PRAGMA foreign_keys=ON')
    cursor.close()
  async with engine.begin() as conn:
    await conn.run_sync(mapper_registry.metadata.create_all)
    await conn.run_sync(outbox_mapper_registry.metadata.create_all)
  async with session_factory() as session:
    yield session
  await engine.dispose()




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
  db_session.add(Product(product_id=1, name='Schab Drogi', brand_name='Auchan', nutrition_facts=NutritionFacts(kcal=300, reference_quantity=ReferenceQuantity(amount=100, unit='g'), nutrients=Nutrients(fat=100)), name_search_standard='schab drogi', category_assignments={1:CategoryAssignment(category_id=4), 2:CategoryAssignment(category_id=9)}))
  db_session.add(Product(product_id=2, name='Schab Tani', brand_name='Rambert', nutrition_facts=NutritionFacts(kcal=250, reference_quantity=ReferenceQuantity(amount=100, unit='g'), nutrients=Nutrients(fat=120)), name_search_standard='schab tani', category_assignments={1:CategoryAssignment(category_id=4)}))
  db_session.add(Product(product_id=3, name='Schab Średni', brand_name='XYZ', nutrition_facts=NutritionFacts(kcal=400, reference_quantity=ReferenceQuantity(amount=100, unit='g'), nutrients=Nutrients(fat=90)), name_search_standard='schab sredni', category_assignments={1:CategoryAssignment(category_id=4)}))
  db_session.add(Product(product_id=4, name='Tofu', brand_name='XYZ', nutrition_facts=NutritionFacts(kcal=300, reference_quantity=ReferenceQuantity(amount=100, unit='g'), nutrients=Nutrients(fat=40)), name_search_standard='tofu', category_assignments={1:CategoryAssignment(category_id=2)}))
  db_session.add(Product(product_id=5, name='Groszek', brand_name='ABC', nutrition_facts=NutritionFacts(kcal=100, reference_quantity=ReferenceQuantity(amount=100, unit='g'), nutrients=Nutrients(fat=100)), name_search_standard='groszek', category_assignments={1:CategoryAssignment(category_id=2)}))
  db_session.add(Product(product_id=6, name='Boczek Kaszubski', brand_name='WWW', nutrition_facts=NutritionFacts(kcal=500, reference_quantity=ReferenceQuantity(amount=100, unit='g'), nutrients=Nutrients(fat=100)), name_search_standard='boczek kaszubski', category_assignments={1:CategoryAssignment(category_id=5)}))
  db_session.add(Product(product_id=7, name='Boczek Cielęcy', brand_name='YYY', nutrition_facts=NutritionFacts(kcal=400, reference_quantity=ReferenceQuantity(amount=100, unit='g'), nutrients=Nutrients(fat=100)), name_search_standard='boczek cielecy', category_assignments={1:CategoryAssignment(category_id=5)}))
  db_session.add(Product(product_id=8, name='Raw Energy Baton kakaowy Bombus', brand_name='WWW', nutrition_facts=NutritionFacts(kcal=300, reference_quantity=ReferenceQuantity(amount=100, unit='g'), nutrients=Nutrients(fat=100)), name_search_standard='raw energy baton kakaowy bombus', category_assignments={1:CategoryAssignment(category_id=2)}))

  db_session.add(CategoryAssignmentTask(task_id=1, product_id=2, hierarchy_id=3, status=CategoryAssignmentTaskStatus.PENDING, user_id=1))
  db_session.add(CategoryAssignmentTask(task_id=2, product_id=3, hierarchy_id=3, status=CategoryAssignmentTaskStatus.PENDING, user_id=2))

  db_session.add(CategoryAssignmentTask(task_id=3, product_id=2, hierarchy_id=2, status=CategoryAssignmentTaskStatus.PENDING, user_id=1))
  db_session.add(CategoryAssignmentTask(task_id=4, product_id=3, hierarchy_id=2, status=CategoryAssignmentTaskStatus.PENDING, user_id=2))

  await db_session.flush()

  db_session.add(ProductIssue(issue_id=1, product_id=1, reported_field=ReportedField.KCAL, status=ProductIssueStatus.PENDING, old_value='300'))
  db_session.add(ProductIssue(issue_id=2, product_id=1, reported_field=ReportedField.FAT, status=ProductIssueStatus.CONFIRMED, resolved_value=120))
  db_session.add(ProductIssue(issue_id=3, product_id=1, reported_field=ReportedField.SUGARS, status=ProductIssueStatus.PENDING))
  db_session.add(ProductIssue(issue_id=4, product_id=2, reported_field=ReportedField.FAT, status=ProductIssueStatus.REJECTED))
  db_session.add(ProductIssue(issue_id=5, product_id=2, reported_field=ReportedField.NAME, status=ProductIssueStatus.PENDING))

  db_session.add(ProductReport(report_id=1, product_id=1, reported_items=[
    ProductReportItem(reported_field=ReportedField.KCAL, proposed_value=120, issue_id=1),
    ProductReportItem(reported_field=ReportedField.FAT, issue_id=2)
    ], user_id=20, product_version=1))
  db_session.add(ProductReport(report_id=2, product_id=1, reported_items=[
    ProductReportItem(reported_field=ReportedField.KCAL, proposed_value=120, issue_id=1)
    ], user_id=10, product_version=1))
  db_session.add(ProductReport(report_id=3, product_id=1, reported_items=[
    ProductReportItem(reported_field=ReportedField.KCAL, proposed_value=121, issue_id=1)
    ], user_id=30, product_version=1))
  await db_session.commit()
  await db_session.close()

@pytest_asyncio.fixture
async def user_roles_repository(db_session):
  return SqlAlchemyUserRolesRepository(db_session)

@pytest_asyncio.fixture
async def access_service(user_roles_repository):
  return AccessService(user_roles_repository)

@pytest_asyncio.fixture
async def access_api(access_service):
  return AccessApi(access_service)

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
def outbox_dao(db_session):
  return OutboxDAO(db_session)

@pytest_asyncio.fixture
def product_issue_confirmation_saga_repository(db_session):
  return SqlAlchemyProductIssueConfirmationSagaRepository(db_session)

@pytest_asyncio.fixture
def plan_hierarchy_for_publication_saga_repository(db_session):
  return SqlAlchemyPlanHierarchyForPublicationSagaRepository(db_session)

@pytest_asyncio.fixture
async def outbox_handler(db_session, outbox_dao):
  return OutboxSubscriber(outbox_dao).handle


@pytest_asyncio.fixture
async def message_publisher():
  subscriber = OutboxSubscriber()
  publisher = DomainMessagePublisher()
  publisher.global_subscribe(subscriber)
  return publisher

@pytest_asyncio.fixture
async def double_message_publisher():
  subscriber = DoubleOutboxSubscriber()
  publisher = DomainMessagePublisher()
  publisher.global_subscribe(subscriber)
  return publisher

@pytest_asyncio.fixture
def unit_of_work(session_factory):
  return SqlAlchemyUnitOfWork(session_factory)

@pytest_asyncio.fixture
def unit_of_work_factory(session_factory):
  return SqlAlchemyUnitOfWorkFactory(session_factory)

@pytest_asyncio.fixture
def product_issue_service(unit_of_work, fake_access_adapter, message_publisher):
  return ProductIssueService(unit_of_work, fake_access_adapter, message_publisher)

@pytest_asyncio.fixture
def product_report_service(unit_of_work, fake_access_adapter, message_publisher):
  return ProductReportService(unit_of_work, fake_access_adapter, message_publisher)

@pytest_asyncio.fixture
def product_issue_repository(db_session):
  return SqlAlchemyProductIssueRepository(db_session)

@pytest_asyncio.fixture
def product_management_service(unit_of_work, fake_access_adapter, message_publisher):
  return ProductManagementService(unit_of_work, fake_access_adapter, message_publisher)

@pytest_asyncio.fixture
def product_hierarchy_management_service(unit_of_work, fake_access_adapter, message_publisher):
  return CategoryHierarchyManagementService(unit_of_work, fake_access_adapter, message_publisher)

@pytest_asyncio.fixture
def category_assignment_task_repository(db_session):
  return SqlAlchemyCategoryAssignmentTaskRepository(db_session)

@pytest_asyncio.fixture
def product_repository(db_session):
  return SqlAlchemyProductRepository(db_session)


