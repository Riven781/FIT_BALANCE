from itertools import count
from operator import ge
from typing import Annotated
import re
from fastapi import Depends, HTTPException

from api.dependencies.filters import PaginationFilters, ProductsFilters
from api.enums import product
from api.enums.product import NameMode, ViewMode
from api.repository.aiosqlite.product import ProductRepository
from api.repository.errors.errors import CheckViolationError, ForeignKeyViolationError, NotNullViolationError, RepositoryError, UniqueViolationError
from api.schemas.product import ProductCreate, ProductDetail, ProductModel, ProductSummary, ProductUpdate
from api.services.errors.errors import  InvalidProductCategoryId, InvalidProductDataError, ProductNotFoundError

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
  def __init__(self, product_repository : ProductRepository) -> ProductDetail:
    self.product_repository = product_repository
  
  async def get(self, product_id: int):
    """
    Return product details by product ID.
    Raises:
      ProductNotFoundError: If the product does not exist.
    """
    product = await self.product_repository.get_by_id(product_id)
    if product is None:
      raise ProductNotFoundError()
    return product

  async def get_all(self, product_filters : ProductsFilters, pagination_filters: PaginationFilters) -> list[ProductDetail]:
    """
    Return the total count of found products and a list of product details
    that match the pagination restrictions.

    Return 0 and an empty list if no products match the filters.
    """
    if product_filters.name is not None:
      if re.fullmatch(r'\s*', product_filters.name):
        return 0, []
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
  
  async def _handle_repository_data_error(self, e):
    await self.product_repository.rollback()
    if isinstance(e, ForeignKeyViolationError):
      raise InvalidProductCategoryId("Product category id is invalid") from e
    if isinstance(e, (NotNullViolationError, CheckViolationError, UniqueViolationError)):
      raise InvalidProductDataError("Product data are invalid") from e
    raise e
    

  async def create(self, product: ProductCreate): 
    product_dict = product.model_dump()
    product_dict['name_search_standard'] = product.name.lower().translate(str.maketrans(POLISH_CHARS))
    product_model = ProductModel(**product_dict)
    try:
      id_created = await self.product_repository.insert(product_model)
      product_created = await self.product_repository.get_by_id(id_created)
      await self.product_repository.commit()
      return product_created
    except RepositoryError as e:
      await self._handle_repository_data_error(e)

  async def delete(self, id):
    try:
      count = await self.product_repository.delete(id)
      if count == 0:
        raise ProductNotFoundError()
      await self.product_repository.commit()
    except RepositoryError as e:
      await self.product_repository.rollback()
      raise  e 
  
  async def update(self, id, product: ProductUpdate):
    product_dict = product.model_dump(exclude_unset=True)
    if product.name is not None:
      product_dict['name_search_standard'] = product.name.lower().translate(str.maketrans(POLISH_CHARS))
    product_model = ProductModel(**product_dict)
    try:
      count = await self.product_repository.update(id, product_model)
      if count == 0:
        raise ProductNotFoundError()
      product = await self.product_repository.get_by_id(id)
      await self.product_repository.commit()
      return product
    except RepositoryError as e:
      await self._handle_repository_data_error(e)


