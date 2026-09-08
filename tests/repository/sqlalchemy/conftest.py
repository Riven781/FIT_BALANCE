from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import StaticPool, insert, text
from sqlalchemy import event
from product_catalog_context.domain.category_hierarchy.product_category import ProductCategory
from product_catalog_context.domain.category_hierarchy.product_category_hierarchy import ProductCategoryHierarchy
from product_catalog_context.domain.product.nutrition_facts import Nutrients, NutritionFacts, ReferenceQuantity
from product_catalog_context.domain.product.product import Product
from product_catalog_context.domain.product.product_assignment import CategoryAssignment
from product_catalog_context.infrastructure.sql_alchemy_repository.product import SqlAlchemyProductRepository
from shared.database.create_new_db import product_table_query, product_category_node_table_query, product_category_hierarchy_query, product_category_assignment, product_category_closure_query, product_category_assignment_task
from shared.database.create_new_db import fields, report, report_item, issue, user, role, user_role, id_sequence, init_id_seq
import pytest_asyncio
from product_catalog_context.domain.category_hierarchy.product_category_hierarchy_status import ProductCategoryHierarchyStatus
from product_catalog_context.infrastructure.sql_alchemy_repository.mapper import mapper_registry

@pytest_asyncio.fixture
async def db_session():
  engine = create_async_engine(f'sqlite+aiosqlite:///:memory:')
  SessionTest = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
  @event.listens_for(engine.sync_engine, 'connect')
  def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute('PRAGMA foreign_keys=ON')
    cursor.close()
  async with engine.begin() as conn:
    await conn.run_sync(mapper_registry.metadata.create_all)
  async with SessionTest() as session:
    yield session
  await engine.dispose()


@pytest_asyncio.fixture
async def insert_data(db_session: AsyncSession):
  db_session.add(ProductCategoryHierarchy(status=ProductCategoryHierarchyStatus.ACTIVE, product_categories=[
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
  db_session.add(ProductCategoryHierarchy(status=ProductCategoryHierarchyStatus.PLANNED_FOR_PUBLICATION, product_categories=[
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
  db_session.add(ProductCategoryHierarchy(status=ProductCategoryHierarchyStatus.DRAFT, product_categories=[
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

  await db_session.commit()
  await db_session.close()

@pytest_asyncio.fixture
def product_repository(db_session):
  return SqlAlchemyProductRepository(db_session)

