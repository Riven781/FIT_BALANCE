from product_catalog_context.domain.issues.confirmation_saga.commands import ApplyResolvedValueToProduct
from product_catalog_context.application.unit_of_work import UnitOfWork, UnitOfWorkFactory
from product_catalog_context.domain.messages.domain_message_publisher import DomainMessagePublisher


class ApplyResolvedValueToProductHandler:
  def __init__(self, unit_of_work_factory: UnitOfWorkFactory, event_publisher: DomainMessagePublisher):
    self.unit_of_work_factory = unit_of_work_factory
    self.event_publisher = event_publisher
  async def handle(self, command: ApplyResolvedValueToProduct):
    async with self.unit_of_work_factory() as uow:
      product = await uow.products.get_by_id(command.product_id)
      if product is None:
        return
      product.resolve_issue(reported_field=command.reported_field, old_value=command.old_value, new_value=command.resolved_value, saga_id=command.saga_id)
      events = product.pull_events()
      await self.event_publisher.publish(events, uow_context=uow.context())
      await uow.products.save(product)