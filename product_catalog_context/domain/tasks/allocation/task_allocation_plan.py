from dataclasses import dataclass


@dataclass(frozen=True)
class TaskAllocationPlan:
  hierarchy_id: int
  limit_per_user: int
  assigned_editor_ids: list[int]

  @property
  def has_tasks_to_assign(self) -> bool:
    return self.limit_per_user > 0
