from abc import ABC, abstractmethod
from dataclasses import asdict
import re
from product_catalog_context.application.category_assignment_task_service import CategoryAssignmentTaskService
from product_catalog_context.application.product_issue_service import ProductIssueService
from product_catalog_context.application.product_management_service import ProductManagementService
from product_catalog_context.application.product_report_service import ProductReportService
from product_catalog_context.domain.product_category import ProductCategory
from product_catalog_context.domain.product_category_hierarchy import ProductCategoryHierarchy
from product_catalog_context.infrastructure.aiosqlite_repository.category_assignment_task_repository import CategoryAssignmentTaskRepository
from product_catalog_context.infrastructure.aiosqlite_repository.product import ProductRepository
from product_catalog_context.infrastructure.aiosqlite_repository.product_category_hierarchy import ProductCategoryHierarchyRepository
import pytest_asyncio

from product_catalog_context.domain.product import Product
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
        results = [product for product in results if product.current_category_id == filters.get('category_id')]
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

from shared.database.create_new_db import product_table_query, product_category_node_table_query, product_category_hierarchy_query, product_category_assignment, product_category_closure_query, product_category_assignment_task
from shared.database.create_new_db import fields, report, report_item, issue, user, role, user_role, id_sequence, init_id_seq

@pytest_asyncio.fixture
async def db():
  db = await aiosqlite.connect(":memory:") #tworzy nową dla każdego połączenia
  db.row_factory = aiosqlite.Row
  await db.execute("PRAGMA foreign_keys = ON")
  await db.execute(product_table_query)
  await db.execute(product_category_node_table_query)
  await db.execute(product_category_hierarchy_query)
  await db.execute(product_category_assignment)
  await db.execute(product_category_closure_query)
  await db.execute(product_category_assignment_task)
  await db.execute(fields)
  await db.execute(report)
  await db.execute(report_item)
  await db.execute(issue)
  await db.execute(user)
  await db.execute(role)
  await db.execute(user_role)
  await db.execute(id_sequence)
  await db.execute(init_id_seq)

  await db.commit()

  yield db

  await db.close()

@pytest_asyncio.fixture
async def hierarchy_repository(db):
  repo = ProductCategoryHierarchyRepository(db)
  category_1 = ProductCategory(name='Batony', category_id=10, parent_id=None)
  category_2 = ProductCategory(name='Batony proteinowe', category_id=11, parent_id=None)

  await repo.insert(ProductCategoryHierarchy(status='ACTIVE', product_categories=[category_1, category_2]))
  return ProductCategoryHierarchyRepository(db)

@pytest_asyncio.fixture
async def category_assignment_service(db) -> CategoryAssignmentTaskService:
  hierarchy_repo = ProductCategoryHierarchyRepository(db)
  product_repo = ProductRepository(db)
  task_repo = CategoryAssignmentTaskRepository(db)

  return CategoryAssignmentTaskService(category_assignment_task_repository=task_repo, product_category_hierarchy_repository=hierarchy_repo, product_repository=product_repo)

@pytest_asyncio.fixture
async def product_management_service(db) -> CategoryAssignmentTaskService:
  hierarchy_repo = ProductCategoryHierarchyRepository(db)
  product_repo = ProductRepository(db)
  return ProductManagementService(product_repository=product_repo, product_category_hierarchy=hierarchy_repo)



@pytest_asyncio.fixture
async def product_report_service(db) -> ProductReportService:
  async with db.executescript(
    """    
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
  return ProductReportService(report_repo, issue_repo)

@pytest_asyncio.fixture
async def product_issue_service(db) -> ProductReportService:
  async with db.executescript(
    """    
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
  return ProductIssueService(issue_repo)