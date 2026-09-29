from product_catalog_context.application.unit_of_work import UnitOfWorkFactory
from product_catalog_context.domain.category_hierarchy.plan_hiearachy_for_publication_saga.commands import  RollbackToDraft
from product_catalog_context.domain.messages.domain_message_publisher import DomainMessagePublisher


class RollbackToDraftHandler:
  def __init__(self, unit_of_work_factory: UnitOfWorkFactory, event_publisher: DomainMessagePublisher):
    self.unit_of_work_factory = unit_of_work_factory
    self.event_publisher = event_publisher

  async def handle(self, command: RollbackToDraft):
    async with self.unit_of_work_factory() as uow:
      hierarchy = await uow.product_category_hierarchies.get_by_id(command.hierarchy_id)
      hierarchy.rollback_to_draft(command.saga_id)
      events = hierarchy.pull_events()
      await self.event_publisher.publish(events)
      await uow.product_category_hierarchies.save(hierarchy)