from product_catalog_context.domain.tasks.category_assignment_task_status import CategoryAssignmentTaskStatus
from product_catalog_context.domain.errors import CategoryAssignmentTaskBelongsToAnotherUser, TaskCannotBeCompleted, TaskCannotBeCancelled


class CategoryAssignmentTask:
  def __init__(self, product_id, hierarchy_id, user_id, status : CategoryAssignmentTaskStatus, task_id = None):
    self.task_id = task_id
    self.product_id = product_id
    self.hierarchy_id = hierarchy_id
    self.user_id = user_id
    self.status = status

  def complete(self, product_editor_id):
    if product_editor_id != self.user_id:
      raise CategoryAssignmentTaskBelongsToAnotherUser()
    if self.status != CategoryAssignmentTaskStatus.PENDING:
      raise TaskCannotBeCompleted()
    self.status = CategoryAssignmentTaskStatus.COMPLETED

  def cancel(self):
    if self.status != CategoryAssignmentTaskStatus.PENDING:
      raise TaskCannotBeCancelled()
    self.status = CategoryAssignmentTaskStatus.CANCELLED
