from pydantic import BaseModel

from product_catalog_context.domain.tasks.category_assignment_task_status import CategoryAssignmentTaskStatus


class CategoryAssignmentTaskResponse(BaseModel):
  task_id: int
  product_id: int
  hierarchy_id: int
  user_id: int
  status: CategoryAssignmentTaskStatus

class CompleteTaskRequest(BaseModel):
  category_id: int

class TaskAssignmentRequest(BaseModel):
  current_category_id: int
  hierarchy_id: int
  limit: int

class TaskAllocationRequest(BaseModel):
  editor_ids: list[int]
  hierarchy_id: int
