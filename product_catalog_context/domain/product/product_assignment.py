from dataclasses import dataclass


@dataclass
class CategoryAssignment:
  category_id: int
  assigned_by: int = None
