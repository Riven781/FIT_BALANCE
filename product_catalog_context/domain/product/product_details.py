from dataclasses import dataclass
from product_catalog_context.domain.product.nutrition_facts import NutritionFacts


@dataclass
class ProductDetails:
  expected_version: int
  name: str
  brand_name: str
  nutrition_facts: NutritionFacts
  img_src: str | None
  ingredients: str | None = None
  allergy_recommendations: str | None = None