from abc import ABC, abstractmethod
from dataclasses import asdict
import re
import pytest_asyncio

from product_catalog_context.domain.product import Product
from product_catalog_context.infrastructure.aiosqlite_repository.mapper import ProductMapper



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

