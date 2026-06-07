from abc import ABC, abstractmethod
import re
import pytest_asyncio


class FakeRepository(ABC):
  @abstractmethod
  async def get(self, id):
    raise NotImplementedError
  
  @abstractmethod
  async def get_all(self, **filters):
    raise NotImplementedError
  

@pytest_asyncio.fixture
async def fake_product_repository():
  class FakeProductRepository(FakeRepository):
    def __init__(self, product_list):
      self.products = product_list
    async def get(self, id):

      return next((product for product in self.products if product.id == id), None)
    
    async def get_all(self, **filters):
      results = list(self.products)
      if filters.get('category_id'):
        results = [product for product in results if product.category_id == filters.get('category_id')]
      if names := filters.get('names'):
        after_space = [f' {name}' for name in names]
        at_the_beegining = [f'^{name}' for name in names]
        re_statement = [f"{option1}|{option2}" for option1, option2 in zip(after_space, at_the_beegining)] 
        for product in results[:]:
          is_found = all(re.search(rs, product) for rs in re_statement)
          if not is_found:
            results.remove(product)
      return results
  return FakeProductRepository

