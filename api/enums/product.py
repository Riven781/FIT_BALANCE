from enum import Enum


class SortBy(str, Enum):
  KCAL = "kcal"
  NAME = "name"
  ID = "id"

class NameMode(str, Enum):
  CONTAINS = "contains"
  STARTS_WITH = "starts_with"
  EXAC = 'exac'

class ViewMode(str, Enum):
  SUMMARY = 'summary'
  DETAIL = "detail"