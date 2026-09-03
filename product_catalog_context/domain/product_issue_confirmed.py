from dataclasses import dataclass

from product_catalog_context.domain.enums.reported_field import ReportedField


@dataclass
class ProductIssueConfirmed:
  product_id: int
  reported_field: ReportedField
  resolved_value: str | int