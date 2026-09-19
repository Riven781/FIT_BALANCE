from functools import singledispatchmethod

from product_catalog_context.domain.messages.domain_message_publisher import DomainMessagePublisher


class PlanningForPublicationSaga:
  def __init__(self, publisher: DomainMessagePublisher):
    self.publisher = publisher
  @singledispatchmethod
  def handle(self, event):
    raise NotImplementedError()

  @handle.register
  async def _(self, event: CategoryHierarchyPlanningForPublicationStarted):
    await self.publisher.publish(CopyCategoryAssignments(hierarchy_id=event.hierarchy_id))

  @handle.register
  async def _(self, event: ProductAssignmentsCopied):
    await self.publisher.publish(MarkAsPlannedForPublication(hierarchy_id=event.hierarchy_id))

  @handle.register
  async def _(self, event: ProductAssignmentsCopyFailed):
    await self.publisher.publish(RevertToDraft(hierarchy_id=event.hierarchy_id))