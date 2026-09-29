from product_catalog_context.domain.category_hierarchy.plan_hiearachy_for_publication_saga.commands import CopyProductAssignments, MarkAsPlannedForPublication, RollbackToDraft
from product_catalog_context.domain.category_hierarchy.plan_hiearachy_for_publication_saga.saga_status import PlanHierarchyForPublicationSagaStatus


class PlanHierarchyForPublicationSaga:
  def __init__(self, hierarchy_id, status=PlanHierarchyForPublicationSagaStatus.STARTED, saga_id = None):
    self.saga_id = saga_id
    self.status = status
    self.hierarchy_id = hierarchy_id
    self._commands = []

  def start(self):
    if self.status == PlanHierarchyForPublicationSagaStatus.STARTED:
      self._commands.append(CopyProductAssignments(hierarchy_id=self.hierarchy_id, saga_id=self.saga_id))
      self.status = PlanHierarchyForPublicationSagaStatus.COPYING_PRODUCT_ASSIGNMENTS

  def mark_as_planned_for_publication(self):
    if self.status == PlanHierarchyForPublicationSagaStatus.COPYING_PRODUCT_ASSIGNMENTS:
      self._commands.append(MarkAsPlannedForPublication(hierarchy_id=self.hierarchy_id, saga_id=self.saga_id))
      self.status = PlanHierarchyForPublicationSagaStatus.MARKING_HIERARCHY_AS_PLANNED_FOR_PUBLICATION

  def complete(self):
    if self.status == PlanHierarchyForPublicationSagaStatus.MARKING_HIERARCHY_AS_PLANNED_FOR_PUBLICATION:
      self.status = PlanHierarchyForPublicationSagaStatus.COMPLETED

  def handle_message_failure(self, message_name):
    if message_name == CopyProductAssignments.command_type and self.status == PlanHierarchyForPublicationSagaStatus.COPYING_PRODUCT_ASSIGNMENTS:
      self._commands.append(RollbackToDraft(hierarchy_id=self.hierarchy_id, saga_id=self.saga_id))
      self.status = PlanHierarchyForPublicationSagaStatus.ROLLING_BACK_TO_DRAFT

  def fail(self):
    if self.status == PlanHierarchyForPublicationSagaStatus.ROLLING_BACK_TO_DRAFT:
      self.status = PlanHierarchyForPublicationSagaStatus.FAILED

  def pull_commands(self):
    commands = self._commands
    self._commands = []
    return commands