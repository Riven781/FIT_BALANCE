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
      return next((product for product in self.products if product.id == id), None)
    
    
    async def insert(self, product):
      self.products.append(product)
      return product.id
    
    async def update(self, id, updated_product : Product):
      count = 0
      for i, product in enumerate(self.products):
        if id == product.id:
          self.products[i] = updated_product
          count += 1
      return count
    
    async def delete(self, id):
      count = 0
      for i, product in enumerate(self.products):
        if id == product.id:
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
      return next((product for product in self.products if product.id == id), None)

    async def get_detail_by_filters(self, **filters):
      results = list(self.products)
      if filters.get('category_id'):
        results = [product for product in results if product.category_id == filters.get('category_id')]
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


