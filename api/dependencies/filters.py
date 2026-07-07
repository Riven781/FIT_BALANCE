from enum import Enum
from typing import Literal
from fastapi import Query

from api.enums.product import NameMode, SortBy, ViewMode

class ProductsFilters:
  def __init__(
      self,
      name: str | None = None,
      #name_mode: NameMode = NameMode.CONTAINS,
      #view_mode: ViewMode = ViewMode.SUMMARY,
      sort_by: SortBy = SortBy.ID,
      order: Literal["asc", "desc"] = "asc",
      category_id: int | None = None
    ):
    self.name = name
    #self.name_mode = name_mode
    #self.view_mode = view_mode
    self.sort_by = sort_by
    self.order = order
    self.category_id = category_id

class PaginationFilters:
  def __init__(
      self,
      page: int = Query(default=1, ge=1),
      limit: int = Query(default=20, ge=1)
    ):
    self.page = page
    self.limit  = limit

class ProductCategoryDeleteFilters:
  def __init__(
      self,
      with_subcategories: bool = False):
    self.with_subcategories = with_subcategories
    