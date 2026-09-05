from enum import StrEnum


class ProductIssueStatus(StrEnum):
  PENDING = 'pending'
  REJECTED = 'rejected'
  CONFIRMED = 'confirmed'
  OBSOLETE = 'obsolete' #it was resolved earlier becuse versions are bad