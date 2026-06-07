from abc import ABC, abstractmethod
import re
import pytest_asyncio


class FakeRepository(ABC):
  @abstractmethod
  async def get_by_id(self, id):
    raise NotImplementedError
  
  @abstractmethod
  async def get_by_filters(self, **filters):
    raise NotImplementedError
  

@pytest_asyncio.fixture
async def fake_product_repository():
  class FakeProductRepository(FakeRepository):
    def __init__(self, product_list):
      self.products = product_list
    async def get_by_id(self, id):

      return next((product for product in self.products if product.id == id), None)
    


    
    async def get_by_filters(self, **filters):
      print(filters)
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
      return len(await self.get_by_filters(**filters))

  return FakeProductRepository

