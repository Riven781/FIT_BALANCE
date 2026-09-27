from dataclasses import dataclass
from product_catalog_context.domain.enums.reported_field import ReportedField


@dataclass
class ProductReportCommand:
  product_id: int
  reported_items: list["ReportedItem"]

@dataclass
class ReportedItem:
  reported_field : ReportedField
  proposed_value: None | str = None
  old_value: None | str = None
