from dataclasses import dataclass
from typing import ClassVar

from product_catalog_context.domain.messages.message import DomainCommand


@dataclass
class PlanHierarchyForPublicationCommand(DomainCommand):
  saga_type: ClassVar[str] = 'plan_hierarchy_for_publication_saga'

@dataclass
class CopyProductAssignments(PlanHierarchyForPublicationCommand):
  hierarchy_id: int
  command_type: ClassVar[str] = 'copy_product_assignments'


@dataclass
class MarkAsPlannedForPublication(PlanHierarchyForPublicationCommand):
  hierarchy_id: int
  command_type: ClassVar[str] = 'mark_as_planned_for_publication'

@dataclass
class RollbackToDraft(PlanHierarchyForPublicationCommand):
  hierarchy_id: int
  command_type: ClassVar[str] = 'rollback_to_draft'
