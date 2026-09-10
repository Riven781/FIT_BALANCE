from abc import ABC, abstractmethod

from product_catalog_context.domain.reports.product_report import ProductReport


class ProductReportRepository(ABC):
  @abstractmethod
  async def get_by_id(self, report_id) -> ProductReport | None:
    pass

  @abstractmethod
  async def save(self, product_report: ProductReport):
    pass

  @abstractmethod
  async def delete(self, product_report: ProductReport):
    pass