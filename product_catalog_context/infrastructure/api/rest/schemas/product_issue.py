from pydantic import BaseModel

from product_catalog_context.domain.enums.reported_field import ReportedField


class ConfirmIssueRequest(BaseModel):
  resolved_value: str | int

class ProductIssueResponse(BaseModel):
  issue_id: int
  product_id: int
  reported_field: ReportedField
  resolved_value: str | int | None
  resolved_by: int | None
  old_value: int | str | None