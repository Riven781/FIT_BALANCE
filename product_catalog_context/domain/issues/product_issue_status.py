from enum import StrEnum


class ProductIssueStatus(StrEnum):
  PENDING = 'pending'
  REJECTED = 'rejected'
  CONFIRMATION_PENDING = 'confirmation_pending'
  CONFIRMED = 'confirmed'
  OBSOLETE = 'obsolete' #it was resolved earlier becuse versions are bad