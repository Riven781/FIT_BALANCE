from pydantic import BaseModel
from product_catalog_context.application.command.product_report import ProductReportCommand, ReportedItem
from product_catalog_context.domain.enums.reported_field import ReportedField
from product_catalog_context.domain.reports.product_report_item_status import ProductReportItemStatus


class ReportedItemModel(BaseModel):
  reported_field : ReportedField
  proposed_value: None | str = None
  old_value: None | str = None


class ProductReportRequest(BaseModel):
  product_id: int
  reported_items: list[ReportedItemModel]

  def to_command(self):
    reported_items = [ReportedItem(item.reported_field, item.proposed_value, item.old_value) for item in self.reported_items]
    return ProductReportCommand(self.product_id, reported_items=reported_items)

class ReportedItemResponse(BaseModel):
  reported_field : ReportedField
  proposed_value: None | str = None
  old_value: None | str = None
  issue_id: int | None
  status: ProductReportItemStatus | None

class ProductReportResponse(BaseModel):
  report_id: int
  reported_items: list[ReportedItemResponse]
  product_id: int
  user_id : int | None
  product_version: int
