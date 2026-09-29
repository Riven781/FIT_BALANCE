from abc import ABC, abstractmethod

from product_catalog_context.domain.category_hierarchy.plan_hiearachy_for_publication_saga.plan_hierarchy_for_publication_saga import PlanHierarchyForPublicationSaga


class PlanHierarchyForPublicationSagaRepository(ABC):
  @abstractmethod
  async def get_by_id(self, saga_id) -> PlanHierarchyForPublicationSaga | None:
    pass

  @abstractmethod
  async def save(self, saga: PlanHierarchyForPublicationSaga):
    pass

  @abstractmethod
  async def next_id(self):
    pass