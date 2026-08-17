from enum import StrEnum


class CategoryAssignmentTaskStatus(StrEnum):
  PENDING = 'PENDING'
  COMPLETED = 'COMPLETED'
  CANCELLED = 'CANCELLED'