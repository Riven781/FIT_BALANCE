from dataclasses import asdict
from itertools import count
from operator import ge
from typing import Annotated
import re

from click import command
from fastapi import Depends, HTTPException

from product_catalog_context.application.command.product import PaginationFiltersCommand, ProductCommand, ProductsFiltersCommand
from product_catalog_context.application.query.product_detail import PublicProductDetail
from product_catalog_context.application.unit_of_work import UnitOfWork
from product_catalog_context.application.utils.shallow_asdict import shallow_asdict
from product_catalog_context.domain.messages.domain_message_publisher import DomainMessagePublisher
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
  def __init__(self, unit_of_work: UnitOfWork, access_adapter: AccessAdapter, event_publisher: DomainMessagePublisher=None):
    self.unit_of_work = unit_of_work
    self.access_adapter = access_adapter
    self.event_publisher = event_publisher
  

  async def create(self, product_command: ProductCommand, product_editor_id):
    product_editor = await self.access_adapter.get_product_editor_for(product_editor_id)
    if product_editor is None:
      raise AccessDenied()
    async with self.unit_of_work as uow:
      category_assignments={}
      if product_command.current_category_id is not None:
        active_hierarchy = await uow.product_category_hierarchies.get_active()
        if not active_hierarchy.contains_product_category(product_command.current_category_id):
          raise CategoryDoesNotBelongToActiveHierarchy()
        category_assignments[active_hierarchy] = (CategoryAssignment(category_id=product_command.current_category_id, assigned_by=product_editor_id))
        #category_assignments[active_hierarchy] = product_command.current_category_id
      if product_command.planned_category_id is not None:
        planned_hierarchy = await uow.product_category_hierarchies.get_planned_for_publication()
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

      await uow.products.save(product)
    return product
    

  async def delete(self, product_id, product_editor_id):
    product_editor = await self.access_adapter.get_product_editor_for(product_editor_id)
    if product_editor is None:
      raise AccessDenied()
    async with self.unit_of_work as uow:
      product = await uow.products.get_by_id(product_id)
      if product is None:
        raise ProductNotFoundError()
      await uow.products.delete(product)
        
    
  
  async def update(self, product_id, product_command: ProductCommand, product_editor_id):  #planned category changed (for productassignemnttask), current category changed (for product issue)
    product_editor = await self.access_adapter.get_product_editor_for(product_editor_id)
    if product_editor is None:
      raise AccessDenied()

    async with self.unit_of_work as uow:
      product = await uow.products.get_by_id(product_id)
      if product is None:
        raise ProductNotFoundError()
  
      if product_command.current_category_id is not None:
        active_hierarchy = await uow.product_category_hierarchies.get_active()
        if not active_hierarchy.contains_product_category(product_command.current_category_id):
          raise CategoryDoesNotBelongToActiveHierarchy()
        product.assign_to_category(active_hierarchy.hierarchy_id, product_command.current_category_id, product_editor_id)

      if product_command.planned_category_id is not None:
        planned_hierarchy = await uow.product_category_hierarchies.get_planned_for_publication()
        if not planned_hierarchy:
          raise PlannedHierarchyDoesNotExist()
        if not planned_hierarchy.contains_product_category(product_command.planned_category_id):
          raise CategoryDoesNotBelongToPlannedHierarchy()
        product.assign_to_category(planned_hierarchy.hierarchy_id, product_command.planned_category_id, product_editor_id)

      data_dict = shallow_asdict(product_command)
      product.update_details(data_dict, product_editor_id)


      await uow.products.save(product)
      events = product.pull_events()

    if self.event_publisher:
      self.event_publisher.publish(events) #not in the same transaction!

    return product


  async def get(self, product_id):
    async with self.unit_of_work as uow:
      product = await uow.products.get_by_id(product_id)
      if product is None:
        raise ProductNotFoundError()
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
