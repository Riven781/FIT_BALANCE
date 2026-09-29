from functools import singledispatch, singledispatchmethod

from product_catalog_context.application.unit_of_work import UnitOfWorkFactory
from product_catalog_context.domain.category_hierarchy.events import HierarchyPlannedForPublication, HierarchyRevertedToDraft, HierarchyRolledBackToDraft, PlanningForPublicationStarted
from product_catalog_context.domain.category_hierarchy.plan_hiearachy_for_publication_saga.plan_hierarchy_for_publication_saga import PlanHierarchyForPublicationSaga
from product_catalog_context.domain.issues.events import MessageExecutionFailed
from product_catalog_context.domain.messages.domain_message_publisher import DomainMessagePublisher
from product_catalog_context.domain.product.events import ProductAssignmentCopied


class PlanHierarchyForPublicationSagaService:
  def __init__(self, publisher: DomainMessagePublisher, unit_of_work_factory: UnitOfWorkFactory):
    self.publisher = publisher
    self.unit_of_work_factory = unit_of_work_factory

  @singledispatchmethod
  def handle(self, event):
    raise NotImplementedError()

  @handle.register
  async def _(self, event: PlanningForPublicationStarted):
    async with self.unit_of_work_factory() as uow:
      saga_id = await uow.plan_hierarchy_for_publication_sagas.next_id()
      saga = PlanHierarchyForPublicationSaga(saga_id=saga_id, hierarchy_id = event.hierarchy_id)
      saga.start()
      commands = saga.pull_commands()
      await self.publisher.publish(messages=commands, uow_context=uow.context())
      await uow.plan_hierarchy_for_publication_sagas.save(saga)

  @handle.register
  async def _(self, event: ProductAssignmentCopied):
    async with self.unit_of_work_factory() as uow:
      saga = await uow.plan_hierarchy_for_publication_sagas.get_by_id(event.saga_id)
      saga.mark_as_planned_for_publication()
      commands = saga.pull_commands()
      await self.publisher.publish(messages=commands, uow_context=uow.context())
      await uow.plan_hierarchy_for_publication_sagas.save(saga)

  @handle.register
  async def _(self, event: HierarchyPlannedForPublication):
    async with self.unit_of_work_factory() as uow:
      saga = await uow.plan_hierarchy_for_publication_sagas.get_by_id(event.saga_id)
      saga.complete()
      await uow.plan_hierarchy_for_publication_sagas.save(saga)

  @handle.register
  async def _(self, event: MessageExecutionFailed):
    async with self.unit_of_work_factory() as uow:
      saga = await uow.plan_hierarchy_for_publication_sagas.get_by_id(event.saga_id)
      saga.handle_message_failure()
      await uow.plan_hierarchy_for_publication_sagas.save(saga)

  @handle.register
  async def _(self, event: HierarchyRolledBackToDraft):
    async with self.unit_of_work_factory() as uow:
      saga = await uow.plan_hierarchy_for_publication_sagas.get_by_id(event.saga_id)
      saga.fail()
      await uow.plan_hierarchy_for_publication_sagas.save(saga)