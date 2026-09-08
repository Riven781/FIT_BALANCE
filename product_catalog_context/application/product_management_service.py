from dataclasses import asdict
from itertools import count
from operator import ge
from typing import Annotated
import re

from click import command
from fastapi import Depends, HTTPException

from product_catalog_context.application.command.product import PaginationFiltersCommand, ProductCommand, ProductsFiltersCommand
from product_catalog_context.application.query.product_detail import PublicProductDetail
from product_catalog_context.application.utils.shallow_asdict import shallow_asdict
from product_catalog_context.infrastructure.adapters.event_dispatcher import EventDispatcher
from product_catalog_context.domain.product.product import Product
from product_catalog_context.domain.services.text_converter import tokenize_for_search
from product_catalog_context.infrastructure.adapters.access_adapter import AccessAdapter
from product_catalog_context.infrastructure.aiosqlite_queries.product import ProductQueries
from product_catalog_context.domain.enums import product_searching
from product_catalog_context.infrastructure.aiosqlite_repository.product import ProductRepository
from product_catalog_context.infrastructure.aiosqlite_repository.errors.errors import CheckViolationError, ForeignKeyViolationError, NotNullViolationError, RepositoryError, UniqueViolationError
from product_catalog_context.application.errors.errors import  AccessDenied, CategoryDoesNotBelongToActiveHierarchy, CategoryDoesNotBelongToPlannedHierarchy, CategoryHierarchyDoesNotExist, InvalidProductCategoryId, InvalidProductDataError, PlannedHierarchyDoesNotExist, ProductNotFoundError
from product_catalog_context.infrastructure.aiosqlite_repository.product_category_hierarchy import ProductCategoryHierarchyRepository
from product_catalog_context.domain.product.product_assignment import CategoryAssignment



class ProductManagementService():
  def __init__(self, product_repository : ProductRepository, product_category_hierarchy_repository : ProductCategoryHierarchyRepository, access_adapter: AccessAdapter, event_dispatcher: EventDispatcher=None):
    self.product_repository = product_repository
    self.product_category_hierarchy_repository = product_category_hierarchy_repository
    self.access_adapter = access_adapter
    self.event_dispatcher = event_dispatcher
  
  
  async def _handle_repository_data_error(self, e):
    await self.product_repository.rollback()
    if isinstance(e, ForeignKeyViolationError):
      raise InvalidProductCategoryId("Product category id is invalid") from e
    if isinstance(e, (NotNullViolationError, CheckViolationError, UniqueViolationError)):
      raise InvalidProductDataError("Product data are invalid") from e
    raise e
    

  async def create(self, product_command: ProductCommand, product_editor_id):
    product_editor = await self.access_adapter.get_product_editor_for(product_editor_id)
    if product_editor is None:
      raise AccessDenied()
    
    category_assignments={}
    if product_command.current_category_id is not None:
      active_hierarchy = await self.product_category_hierarchy_repository.get_active()
      if not active_hierarchy.contains_product_category(product_command.current_category_id):
        raise CategoryDoesNotBelongToActiveHierarchy()
      category_assignments[active_hierarchy] = (CategoryAssignment(category_id=product_command.current_category_id, assigned_by=product_editor_id))
      #category_assignments[active_hierarchy] = product_command.current_category_id
    if product_command.planned_category_id is not None:
      planned_hierarchy = await self.product_category_hierarchy_repository.get_planned_for_publication()
      if not planned_hierarchy:
        raise PlannedHierarchyDoesNotExist()
      if not planned_hierarchy.contains_product_category(product_command.planned_category_id):
        raise CategoryDoesNotBelongToPlannedHierarchy()
      category_assignments[planned_hierarchy] = (CategoryAssignment(category_id=product_command.planned_category_id, assigned_by=product_editor_id))
      #category_assignments[planned_hierarchy] = product_command.planned_category_id

    product = Product(
      name=product_command.name,
      brand_name=product_command.brand_name,
      nutrition_facts=product_command.nutrition_facts,
      ingredients=product_command.ingredients,
      allergy_recommendations=product_command.allergy_recommendations,
      created_by=product_editor_id,
      category_assignments=category_assignments
    )
    try:
      id_created = await self.product_repository.insert(product)
      product_created = await self.product_repository.get_by_id(id_created)
      await self.product_repository.commit()
      return product_created
    except RepositoryError as e:
      await self._handle_repository_data_error(e)

  async def delete(self, product_id, product_editor_id):
    product_editor = await self.access_adapter.get_product_editor_for(product_editor_id)
    if product_editor is None:
      raise AccessDenied()
    try:
      count = await self.product_repository.delete(product_id)
      if count == 0:
        raise ProductNotFoundError()
      await self.product_repository.commit()
    except RepositoryError as e:
      await self.product_repository.rollback()
      raise  e 
  
  async def update(self, product_id, product_command: ProductCommand, product_editor_id):  #planned category changed (for productassignemnttask), current category changed (for product issue)
    product_editor = await self.access_adapter.get_product_editor_for(product_editor_id)
    if product_editor is None:
      raise AccessDenied()
    try:
      product = await self.product_repository.get_by_id(product_id)
    except RepositoryError as e:
      await self._handle_repository_data_error(e)
  
    if product is None:
      raise ProductNotFoundError()

    if product_command.current_category_id is not None:
      active_hierarchy = await self.product_category_hierarchy_repository.get_active()
      if not active_hierarchy.contains_product_category(product_command.current_category_id):
        raise CategoryDoesNotBelongToActiveHierarchy()
      product.assign_to_category(active_hierarchy.hierarchy_id, product_command.current_category_id, product_editor_id)

    if product_command.planned_category_id is not None:
      planned_hierarchy = await self.product_category_hierarchy_repository.get_planned_for_publication()
      if not planned_hierarchy:
        raise PlannedHierarchyDoesNotExist()
      if not planned_hierarchy.contains_product_category(product_command.planned_category_id):
        raise CategoryDoesNotBelongToPlannedHierarchy()
      product.assign_to_category(planned_hierarchy.hierarchy_id, product_command.planned_category_id, product_editor_id)

    data_dict = shallow_asdict(product_command)
    product.update_details(data_dict, product_editor_id)

    try:
      await self.product_repository.update(product_id, product)
      events = product.pull_events()
      if self.event_dispatcher:
        self.event_dispatcher.dispatch(events) #not in the same transaction!

      return product
    except RepositoryError as e:
      await self._handle_repository_data_error(e)

  async def get(self, product_id):
    try:
      product = await self.product_repository.get_by_id(product_id)
      if product is None:
        raise ProductNotFoundError()
    except RepositoryError as e:
      await self._handle_repository_data_error(e)
    return product

  """ 
  async def assign_planned_category(self, product_id, alternative_category_id):
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
  """
