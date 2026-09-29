from product_catalog_context.application.unit_of_work import UnitOfWorkFactory
from product_catalog_context.domain.category_hierarchy.plan_hiearachy_for_publication_saga.commands import CopyProductAssignments
from product_catalog_context.domain.messages.domain_message_publisher import DomainMessagePublisher
from product_catalog_context.domain.product.events import ProductAssignmentCopied


class CopyProductAssignmentsHandler:
  def __init__(self, unit_of_work_factory: UnitOfWorkFactory, event_publisher: DomainMessagePublisher):
    self.unit_of_work_factory = unit_of_work_factory
    self.event_publisher = event_publisher

  async def handle(self, command: CopyProductAssignments):
    async with self.unit_of_work_factory() as uow:
      active_hierarchy = await uow.product_category_hierarchies.get_active()
      await uow.products.copy_category_assignments(active_hierarchy_id=active_hierarchy.hierarchy_id, draft_hierarchy_id=command.hierarchy_id)
      await self.event_publisher.publish([ProductAssignmentCopied(saga_id = command.saga_id, hierarchy_id=command.hierarchy_id)], uow_context=uow.context())