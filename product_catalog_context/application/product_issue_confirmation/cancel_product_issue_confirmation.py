from product_catalog_context.application.unit_of_work import UnitOfWork, UnitOfWorkFactory
from product_catalog_context.domain.issues.confirmation_saga.commands import CancelProductIssueConfirmation, ConfirmProductIssue
from product_catalog_context.domain.messages.domain_message_publisher import DomainMessagePublisher

class CancelProductIssueConfirmationHandler:
  def __init__(self, unit_of_work_factory: UnitOfWorkFactory, event_publisher: DomainMessagePublisher):
    self.unit_of_work_factory = unit_of_work_factory
    self.event_publisher = event_publisher

  async def handle(self, command: CancelProductIssueConfirmation):
    async with self.unit_of_work_factory() as uow:
      issue = await uow.product_issues.get_by_id(command.issue_id)
      issue.cancel_confirmation_as_obsolete(command.saga_id)
      events = issue.pull_events()
      await self.event_publisher.publish(events, uow_context=uow.context())
      await uow.product_issues.save(issue)