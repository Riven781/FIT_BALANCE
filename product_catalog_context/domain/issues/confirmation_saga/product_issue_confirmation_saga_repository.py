from abc import ABC, abstractmethod

from product_catalog_context.domain.issues.confirmation_saga.product_issue_confirmation_saga import ProductIssueConfirmationSaga


class ProductIssueConfirmationSagaRepository(ABC):
  @abstractmethod
  async def get_by_id(self, saga_id) -> ProductIssueConfirmationSaga | None:
    pass

  @abstractmethod
  async def save(self, saga: ProductIssueConfirmationSaga):
    pass

  @abstractmethod
  async def next_id(self):
    pass