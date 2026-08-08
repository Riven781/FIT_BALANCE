from dataclasses import dataclass

from product_catalog_context.application.query.category_path_item import CategoryPathItem
from product_catalog_context.domain.nutrition_facts import NutritionFacts

@dataclass
class PublicProductDetail:
  product_id : int
  name: str
  brand_name: str
  nutrition_facts: NutritionFacts
  img_src: str
  category_path: list[CategoryPathItem]


