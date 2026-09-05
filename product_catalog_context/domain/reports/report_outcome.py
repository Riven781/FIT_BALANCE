from enum import StrEnum


class ReportOutcome(StrEnum):
  REJECTED = 'rejected'
  FULLY_CONFIRMED = 'fully_confirmed'
  PARTIALLY_CONFIRMED = 'partially_confirmed'
  IN_REVIEW = 'in_review'
  OBSOLETE = 'obsolete'