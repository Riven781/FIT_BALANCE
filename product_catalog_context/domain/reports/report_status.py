from enum import StrEnum


class ReportStatus(StrEnum):
  UNASSIGNED = 'unassigned'
  PENDING = 'pending'
  PARTIALLY_REVIEWED = 'partially_reviewed'
  REVIEWED = 'reviewed'