import math

from product_catalog_context.domain.category_hierarchy.product_category_hierarchy import ProductCategoryHierarchy
from product_catalog_context.domain.errors import UserIdRequired
from product_catalog_context.domain.tasks.allocation.task_allocation_plan import TaskAllocationPlan


def calculate_allocation_plan(
  hierarchy: ProductCategoryHierarchy,
  unassigned_products_count: int, 
  active_tasks_count: int, 
  editor_ids: list[int]
) -> TaskAllocationPlan:
  hierarchy.ensure_can_assign_tasks()

  if editor_ids == []:
    raise UserIdRequired()

  remaining_products = unassigned_products_count - active_tasks_count
  if remaining_products <= 0:
    return TaskAllocationPlan(hierarchy_id=hierarchy.hierarchy_id, limit_per_user=0, assigned_editor_ids=editor_ids)
  limit_per_user = math.ceil((remaining_products) / len(editor_ids))
  return TaskAllocationPlan(hierarchy_id=hierarchy.hierarchy_id, limit_per_user=limit_per_user, assigned_editor_ids=editor_ids)
