from dataclasses import dataclass
from typing import Literal

from product_catalog_context.domain.enums.product_searching import SortBy
from product_catalog_context.domain.product.nutrition_facts import NutritionFacts
from product_catalog_context.domain.product.product_details import ProductDetails


@dataclass
class ProductCommand:
  name: str
  brand_name: str
  nutrition_facts: NutritionFacts
  img_src: str | None
  current_category_id: int | None
  expected_current_category_version: int = 0
  planned_category_id: int | None = None
  expected_planned_category_version: int = 0
  ingredients: str | None = None
  allergy_recommendations: str | None = None

  def to_details(self) -> ProductDetails:
    return ProductDetails(
      name=self.name,
      brand_name=self.brand_name,
      nutrition_facts=self.nutrition_facts,
      img_src=self.img_src,
      ingredients=self.ingredients,
      allergy_recommendations=self.allergy_recommendations
    )

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