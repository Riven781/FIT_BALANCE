from dataclasses import asdict
from itertools import count
from operator import ge
from typing import Annotated
import re
from fastapi import Depends, HTTPException

from product_catalog_context.application.command.product import PaginationFiltersCommand, ProductCommand, ProductsFiltersCommand
from product_catalog_context.application.query.product_detail import PublicProductDetail
from product_catalog_context.application.utils.shallow_asdict import shallow_asdict
from product_catalog_context.domain.product import Product
from product_catalog_context.domain.services.text_converter import tokenize_for_search
from product_catalog_context.infrastructure.aiosqlite_queries.product import ProductQueries
from product_catalog_context.domain.enums import product_searching
from product_catalog_context.infrastructure.aiosqlite_repository.product import ProductRepository
from product_catalog_context.infrastructure.aiosqlite_repository.errors.errors import CheckViolationError, ForeignKeyViolationError, NotNullViolationError, RepositoryError, UniqueViolationError
from product_catalog_context.application.errors.errors import  InvalidProductCategoryId, InvalidProductDataError, ProductNotFoundError



class ProductManagementService():
  def __init__(self, product_repository : ProductRepository, product_category_hierarchy=None):
    self.product_repository = product_repository
    self.product_category_hierarchy = product_category_hierarchy
  
  async def _handle_repository_data_error(self, e):
    await self.product_repository.rollback()
    if isinstance(e, ForeignKeyViolationError):
      raise InvalidProductCategoryId("Product category id is invalid") from e
    if isinstance(e, (NotNullViolationError, CheckViolationError, UniqueViolationError)):
      raise InvalidProductDataError("Product data are invalid") from e
    raise e
    

  async def create(self, product_command: ProductCommand):
    product = Product(
      name=product_command.name,
      brand_name=product_command.brand_name,
      nutrition_facts=product_command.nutrition_facts,
      current_category_id=product_command.current_category_id,
      ingredients=product_command.ingredients,
      allergy_recommendations=product_command.allergy_recommendations
    )
    try:
      
      id_created = await self.product_repository.insert(product)
      

      product_created = await self.product_repository.get_by_id(id_created)
      await self.product_repository.commit()
      return product_created
    except RepositoryError as e:
      await self._handle_repository_data_error(e)

  async def delete(self, product_id):
    try:
      count = await self.product_repository.delete(product_id)
      if count == 0:
        raise ProductNotFoundError()
      await self.product_repository.commit()
    except RepositoryError as e:
      await self.product_repository.rollback()
      raise  e 
  
  async def update(self, product_id, product_command: ProductCommand):
    try:
      product = await self.product_repository.get_by_id(product_id)
    except RepositoryError as e:
      await self._handle_repository_data_error(e)
  
    if product is None:
      raise ProductNotFoundError()

    data_dict = shallow_asdict(product_command)
    product.update_details(data_dict)


    try:
      await self.product_repository.update(product_id, product)
      return product
    except RepositoryError as e:
      await self._handle_repository_data_error(e)

  async def get(self, product_id):
    try:
      product = await self.product_repository.get_by_id(product_id)
      if product is None:
        raise ProductNotFoundError()
    except RepositoryError as e:
      self._handle_repository_data_error(e)
    return product

  async def assign_alternative_category(self, product_id, alternative_category_id):
    hierarchy = self.product_category_hierarchy.get_planned_for_deploy()
    if hierarchy is None:
      raise ValueError()

    if not hierarchy.is_product_category_in_hierarchy(alternative_category_id):
      raise ValueError()

    product = await self.product_repository.get_by_id(product_id)

    if product is None:
      raise ProductNotFoundError()

    product.assign_alternative_category(alternative_category_id)

    await self.product_repository.update(product)

