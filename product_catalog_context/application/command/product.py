from dataclasses import dataclass
from typing import Literal

from product_catalog_context.domain.enums.product_searching import SortBy
from product_catalog_context.domain.nutrition_facts import NutritionFacts


@dataclass
class ProductCommand:
  name: str
  brand_name: str
  nutrition_facts: NutritionFacts
  img_src: str | None
  current_category_id: int | None
  planned_category_id: int | None = None
  ingredients: str | None = None
  allergy_recommendations: str | None = None

@dataclass
class PaginationFiltersCommand:
  page: int
  limit: int

@dataclass
class ProductsFiltersCommand:
  name: str | None = None
  sort_by: SortBy = SortBy.ID
  order: Literal["asc", "desc"] = 'asc'
  category_id: int | None = None