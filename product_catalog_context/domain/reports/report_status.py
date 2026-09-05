from enum import StrEnum


class ReportStatus(StrEnum):
  PENDING = 'pending'
  PARTIALLY_REVIEWED = 'partially_reviewed'
  REVIEWED = 'reviewed'