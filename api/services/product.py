from itertools import count
from operator import ge
from typing import Annotated
import re
from fastapi import Depends, HTTPException

from api.dependencies.filters import PaginationFilters, ProductsFilters
from api.enums import product
from api.enums.product import NameMode, ViewMode
from api.repository.aiosqlite.product import ProductRepository
from api.schemas.product import ProductCreate, ProductDetail, ProductSummary

POLISH_CHARS = {
    "ą": "a",
    "ć": "c",
    "ę": "e",
    "ł": "l",
    "ń": "n",
    "ó": "o",
    "ś": "s",
    "ż": "z",
    "ź": "z",
    "Ą": "A",
    "Ć": "C",
    "Ę": "E",
    "Ł": "L",
    "Ń": "N",
    "Ó": "O",
    "Ś": "S",
    "Ż": "Z",
    "Ź": "Z",
}
#todo filtracja według najlepszego dopasowania
class ProductService():
  def __init__(self, product_repository : ProductRepository):
    self.product_repository = product_repository
  
  async def get(self, product_id):
    return await self.product_repository.get_by_id(product_id)

  async def get_all(self, product_filters : ProductsFilters, pagination_filters: PaginationFilters):
    if product_filters.name is not None:
      if re.fullmatch(r'\s*', product_filters.name): #option for future: return 0, []
        names = None
      else:
        names = product_filters.name.lower().translate(str.maketrans(POLISH_CHARS)).split()
    else:
      names = None
    category_id = product_filters.category_id

    products = await self.product_repository.get_by_filters(
      category_id=category_id, 
      names=names, sort_by=product_filters.sort_by, 
      order=product_filters.order, 
      page=pagination_filters.page, 
      limit=pagination_filters.limit
    )
    
    total  = await self.product_repository.get_total(category_id=category_id, names=names)
    return total, products

  async def create(self, product: ProductCreate): 
    product.name_search_standard = product.name.lower().translate(str.maketrans(POLISH_CHARS))
    try:
      id_created = await self.product_repository.insert(product)
      product_created = await self.product_repository.get_by_id(id_created)
      await self.product_repository.commit()
      return product_created
    except Exception as e:
      print(e)
      await self.product_repository.rollback()
      raise

  async def delete(self, id):
    try:
      count = await self.product_repository.delete(id)
      if count == 0:
        raise HTTPException(404, 'Not Found')
      await self.product_repository.commit()
    except Exception:
      await self.product_repository.rollback()
      raise
  
  async def update(self, id, product):
    product.name_search_standard = product.name.lower().translate(str.maketrans(POLISH_CHARS))

    try:
      count = await self.product_repository.update(id, product)
      if count == 0:
        raise HTTPException(404)
      product = await self.product_repository.get_by_id(id)
      await self.product_repository.commit()
      return product
    except Exception as e:
      print(e)
      await self.product_repository.rollback()
      raise

