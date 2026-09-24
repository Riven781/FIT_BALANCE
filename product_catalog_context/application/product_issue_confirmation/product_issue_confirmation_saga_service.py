from functools import singledispatchmethod

from product_catalog_context.application.unit_of_work import UnitOfWork, UnitOfWorkFactory
from product_catalog_context.domain.issues.confirmation_saga.product_issue_confirmation_saga import ProductIssueConfirmationSaga
from product_catalog_context.domain.issues.events import MessageExecutionFailed, ProductIssueConfirmationCancelledAsObsolete, ProductIssueConfirmationStarted, ProductIssueConfirmed, ProductIssueFailed, ProductIssueResetToPending, ResolvedValueAppliedToProduct
from product_catalog_context.domain.messages.domain_message_publisher import DomainMessagePublisher
from product_catalog_context.domain.product.events import ResolvedValueApplicationRejected


class ProductIssueConfirmationSagaService:
  def __init__(self, publisher: DomainMessagePublisher, unit_of_work_factory: UnitOfWorkFactory):
    self.publisher = publisher
    self.unit_of_work_factory = unit_of_work_factory

  @singledispatchmethod
  def handle(self, event):
    raise NotImplementedError()

  @handle.register
  async def _(self, event : ProductIssueConfirmationStarted):
    async with self.unit_of_work_factory() as uow:
      saga_id = await uow.product_issues_confirmation_sagas.next_id()
      saga = ProductIssueConfirmationSaga(saga_id=saga_id, issue_id=event.issue_id)
      saga.start(event.product_id, event.resolved_value, event.old_value, event.reported_field)
      events = saga.pull_commands()
      print(event)
      await self.publisher.publish(messages=events, uow_context=uow.context())
      await uow.product_issues_confirmation_sagas.save(saga)

  @handle.register
  async def _(self, event : ResolvedValueAppliedToProduct):
    async with self.unit_of_work_factory() as uow:
      saga = await uow.product_issues_confirmation_sagas.get_by_id(event.saga_id)
      saga.confirm()
      events = saga.pull_commands()
      await self.publisher.publish(messages=events, uow_context=uow.context())
      await uow.product_issues_confirmation_sagas.save(saga)

  @handle.register
  async def _(self, event : ResolvedValueApplicationRejected):
    async with self.unit_of_work_factory() as uow:
      saga = await uow.product_issues_confirmation_sagas.get_by_id(event.saga_id)
      saga.cancel()
      events = saga.pull_commands()
      await self.publisher.publish(messages=events, uow_context=uow.context())
      await uow.product_issues_confirmation_sagas.save(saga)


  @handle.register
  async def _(self, event : ProductIssueConfirmed):
    async with self.unit_of_work_factory() as uow:
      saga = await uow.product_issues_confirmation_sagas.get_by_id(event.saga_id)
      saga.complete()
      await uow.product_issues_confirmation_sagas.save(saga)

  @handle.register
  async def _(self, event : ProductIssueConfirmationCancelledAsObsolete):
    async with self.unit_of_work_factory() as uow:
      saga = await uow.product_issues_confirmation_sagas.get_by_id(event.saga_id)
      saga.obsolete()
      await uow.product_issues_confirmation_sagas.save(saga)

  @handle.register
  async def _(self, event : MessageExecutionFailed):
    if event.saga_id is None:
      return
    if event.error_type != 'concurrent_modification':
      return
    async with self.unit_of_work_factory() as uow:
      saga = await uow.product_issues_confirmation_sagas.get_by_id(event.saga_id)
      saga.handle_message_failure(event.message_name)
      events = saga.pull_commands()
      await self.publisher.publish(messages=events, uow_context=uow.context())
      await uow.product_issues_confirmation_sagas.save(saga)

  @handle.register
  async def _(self, event : ProductIssueResetToPending):
    async with self.unit_of_work_factory() as uow:
      saga = await uow.product_issues_confirmation_sagas.get_by_id(event.saga_id)
      saga.reset_completed()
      await uow.product_issues_confirmation_sagas.save(saga)