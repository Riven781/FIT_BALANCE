from typing import Annotated

from fastapi import APIRouter, Depends

from product_catalog_context.application.category_assignment_task_service import CategoryAssignmentTaskService
from product_catalog_context.infrastructure.api.rest.dependencies.database import get_category_assignment_task_service, get_current_user_id
from product_catalog_context.infrastructure.api.rest.schemas.category_assignment_task import  CategoryAssignmentTaskResponse, CompleteTaskRequest, TaskAllocationRequest, TaskAssignmentRequest


category_assignment_tasks_router = APIRouter()

@category_assignment_tasks_router.get("/category-assignment-tasks/{task_id}", response_model=CategoryAssignmentTaskResponse)
async def read_task(
  task_id: int,
  category_assignment_task_service: Annotated[CategoryAssignmentTaskService, Depends(get_category_assignment_task_service)]
):
  return await category_assignment_task_service.get_task(task_id)

@category_assignment_tasks_router.put("/category-assignment-tasks/{task_id}/complete", status_code=204)
async def complete_task(
  task_id: int,
  complete_task_request: CompleteTaskRequest,
  category_assignment_task_service: Annotated[CategoryAssignmentTaskService, Depends(get_category_assignment_task_service)],
  user_id : Annotated[int, Depends(get_current_user_id)],
):
  await category_assignment_task_service.complete_category_assignment(task_id, complete_task_request.category_id ,user_id)

@category_assignment_tasks_router.post("/users/{editor_id}/category-assignment-tasks", status_code=204)
async def assign_tasks_for_user_by_active_category_id(
  editor_id: int,
  request: TaskAssignmentRequest,
  category_assignment_task_service: Annotated[CategoryAssignmentTaskService, Depends(get_category_assignment_task_service)],
  user_id : Annotated[int, Depends(get_current_user_id)],
):
  await category_assignment_task_service.assign_tasks_for_user_by_active_category_id(user_id, editor_id, request.hierarchy_id, request.current_category_id, request.limit)

@category_assignment_tasks_router.post("/category-assignment-task-allocation", status_code=204)
async def allocate_tasks_for_users(
  request: TaskAllocationRequest,
  category_assignment_task_service: Annotated[CategoryAssignmentTaskService, Depends(get_category_assignment_task_service)],
  user_id : Annotated[int, Depends(get_current_user_id)],
):
  await category_assignment_task_service.allocate_tasks_for_users(user_id, request.editor_ids, request.hierarchy_id)

@category_assignment_tasks_router.delete("/category-assignment-tasks/{task_id}", status_code=204)
async def delete_task(
  task_id: int,
  category_assignment_task_service: Annotated[CategoryAssignmentTaskService, Depends(get_category_assignment_task_service)],
  user_id : Annotated[int, Depends(get_current_user_id)]
):
  await category_assignment_task_service.delete_task(task_id, user_id)

@category_assignment_tasks_router.delete("/users/{user_id}/category-assignment-tasks", status_code=204)
async def delete_tasks_by_user(
  user_id: int,
  category_assignment_task_service: Annotated[CategoryAssignmentTaskService, Depends(get_category_assignment_task_service)],
  catalog_manager_id : Annotated[int, Depends(get_current_user_id)]
):
  await category_assignment_task_service.delete_tasks_by_user(catalog_manager_id, user_id)


@category_assignment_tasks_router.delete("/users/{user_id}/category-assignment-tasks/products/{product_id}", status_code=204)
async def delete_task_by_user_and_product(
  user_id: int, product_id: int,
  category_assignment_task_service: Annotated[CategoryAssignmentTaskService, Depends(get_category_assignment_task_service)],
  catalog_manager_id : Annotated[int, Depends(get_current_user_id)]
):
  await category_assignment_task_service.delete_task_by_user_and_product(user_id, product_id, catalog_manager_id)