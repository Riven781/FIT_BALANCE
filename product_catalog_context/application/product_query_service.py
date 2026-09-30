from dataclasses import asdict
from itertools import count
from operator import ge
from typing import Annotated
import re
from fastapi import Depends, HTTPException

from product_catalog_context.application.command.product import PaginationFiltersCommand, ProductCommand, ProductsFiltersCommand
from product_catalog_context.application.query.product_detail import PublicProductDetail
from product_catalog_context.domain.product.product import Product
from product_catalog_context.domain.services.text_converter import tokenize_for_search
from product_catalog_context.domain.enums import product_searching
from product_catalog_context.infrastructure.aiosqlite_queries.product import ProductQueries
from product_catalog_context.infrastructure.aiosqlite_repository.product import ProductRepository
from product_catalog_context.infrastructure.aiosqlite_repository.errors.errors import CheckViolationError, ForeignKeyViolationError, NotNullViolationError, RepositoryError, UniqueViolationError
from product_catalog_context.application.errors.errors import  InvalidProductCategoryId, InvalidProductDataError, ProductNotFoundError


#todo filtracja według najlepszego dopasowania
class ProductQueryService():
  def __init__(self, product_queries : ProductQueries):
    self.product_queries = product_queries
  
  async def get(self, product_id: int) -> PublicProductDetail:
    """
    Return product details by product ID.
    Raises:
      ProductNotFoundError: If the product does not exist.
    """
    product = await self.product_queries.get_detail_by_id(product_id)
    #product = await self.product_repository.get_by_id(product_id)
    if product is None:
      raise ProductNotFoundError()
    return product

  async def get_all(self, product_filters : ProductsFiltersCommand, pagination_filters: PaginationFiltersCommand) -> tuple[int, list[PublicProductDetail]]:
    """
    Return the total count of found products and a list of product details
    that match the pagination restrictions.

    Return 0 and an empty list if no products match the filters.
    """
    if product_filters.name is not None:
      if re.fullmatch(r'\s*', product_filters.name):
        return 0, []
      names = tokenize_for_search(product_filters.name)
    else:
      names = None
    category_id = product_filters.category_id
    print('rrr')
    products = await self.product_queries.get_detail_by_filters(
      category_id=category_id, 
      names=names, sort_by=product_filters.sort_by, 
      order=product_filters.order,
      page=pagination_filters.page,
      limit=pagination_filters.limit
    )
    print('ggg')
    total  = await self.product_queries.get_total(category_id=category_id, names=names)
    return total, products
