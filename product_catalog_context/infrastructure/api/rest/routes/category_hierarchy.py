from typing import Annotated

from fastapi import APIRouter, Depends

from product_catalog_context.application.category_hierarchy_management_service import CategoryHierarchyManagementService
from product_catalog_context.application.command.category_hierarchy import EditHierarchyCommand
from product_catalog_context.infrastructure.api.rest.dependencies.database import get_current_user_id, get_product_hierarchy_category_service
from product_catalog_context.infrastructure.api.rest.schemas.product_category import EditProductCategoryHierarchyRequest, ProductCategoryHierarchyResponse


category_hierarchy_router = APIRouter()

@category_hierarchy_router.get("/category-hierarchy/{hierarchy_id}", response_model=ProductCategoryHierarchyResponse)   #thats only test method 
async def read_hierarchy(
  hierarchy_id: int,
  category_hierarchy_management_service: Annotated[CategoryHierarchyManagementService, Depends(get_product_hierarchy_category_service)]
):
  result = await category_hierarchy_management_service.get_hierarchy(hierarchy_id)
  return result


@category_hierarchy_router.put("/category-hierarchy/{hierarchy_id}", response_model=ProductCategoryHierarchyResponse, status_code=200) 
async def edit_hierarchy(
  hierarchy_id: int,
  hierarchy: EditProductCategoryHierarchyRequest,
  category_hierarchy_management_service: Annotated[CategoryHierarchyManagementService, Depends(get_product_hierarchy_category_service)],
  user_id : Annotated[int, Depends(get_current_user_id)],

):
  return await category_hierarchy_management_service.edit_hierarchy(
    EditHierarchyCommand(
      hierarchy_id=hierarchy_id, 
      existing_categories = hierarchy.existing_categories,
      draft_categories=hierarchy.draft_categories,
      catalog_manager_id=user_id
      ))


@category_hierarchy_router.post("/category-hierarchy/{hierarchy_id}/draft", response_model=ProductCategoryHierarchyResponse, status_code=201) 
async def create_draft_hierarchy(
  hierarchy_id: int,
  user_id : Annotated[int, Depends(get_current_user_id)],
  category_hierarchy_management_service: Annotated[CategoryHierarchyManagementService, Depends(get_product_hierarchy_category_service)]
):
  return await category_hierarchy_management_service.create_draft(hierarchy_id=hierarchy_id, catalog_manager_id=user_id)

@category_hierarchy_router.delete("/category-hierarchy/{hierarchy_id}", status_code=204) 
async def delete_draft_hierarchy(
  hierarchy_id: int,
  user_id : Annotated[int, Depends(get_current_user_id)],
  category_hierarchy_management_service: Annotated[CategoryHierarchyManagementService, Depends(get_product_hierarchy_category_service)]
):
  await category_hierarchy_management_service.delete_draft(hierarchy_id=hierarchy_id, catalog_manager_id=user_id)


@category_hierarchy_router.put("/category-hierarchy/{hierarchy_id}/draft", status_code=204) 
async def revert_hierarchy_to_draft(
  hierarchy_id: int,
  user_id : Annotated[int, Depends(get_current_user_id)],
  category_hierarchy_management_service: Annotated[CategoryHierarchyManagementService, Depends(get_product_hierarchy_category_service)]
):
  await category_hierarchy_management_service.revert_to_draft(hierarchy_id=hierarchy_id, catalog_manager_id=user_id)

@category_hierarchy_router.put("/category-hierarchy/{hierarchy_id}/publish", status_code=204) 
async def publish_hierarchy(
  hierarchy_id: int,
  user_id : Annotated[int, Depends(get_current_user_id)],
  category_hierarchy_management_service: Annotated[CategoryHierarchyManagementService, Depends(get_product_hierarchy_category_service)]
):
  await category_hierarchy_management_service.publish_hierarchy(hierarchy_id=hierarchy_id, catalog_manager_id=user_id)

@category_hierarchy_router.put("/category-hierarchy/{hierarchy_id}/plan-for-publication", status_code=202)
async def plan_hierarchy_for_publication(
  hierarchy_id: int,
  user_id : Annotated[int, Depends(get_current_user_id)],
  category_hierarchy_management_service: Annotated[CategoryHierarchyManagementService, Depends(get_product_hierarchy_category_service)]
):
  await category_hierarchy_management_service.plan_for_publication(hierarchy_id=hierarchy_id, catalog_manager_id=user_id)