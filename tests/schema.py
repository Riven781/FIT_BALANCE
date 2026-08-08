from pydantic import BaseModel


class ProductTest(BaseModel):
  id: int | None = None
  name: str | None = None
  brand_name: str | None = None
  kcal: float |None = None
  brand: str | None = None
  reference_amount: int = 100
  reference_unit: str = 'g'
  img_src: str | None = None
  category_id: int | None = None
  fat: float | None = None
  saturates: float | None = None
  carbohydrates: float | None = None
  sugars: float | None = None
  protein: float | None = None
  salt: float | None = None
  fiber: float | None = None
  ingredients: str | None = None
  allergy_recommendations: str | None = None
  name_search_standard: str | None = None


class ProductTestStrKcal(BaseModel):
  id: int | None = None
  name: str | None = None
  kcal: str |None = None
  brand: str | None = None
  reference_amount: int = 100
  reference_unit: str = 'g'
  img_src: str | None = None
  category_id: int | None = None
  fat: float | None = None
  saturates: float | None = None
  carbohydrates: float | None = None
  sugars: float | None = None
  protein: float | None = None
  salt: float | None = None
  fiber: float | None = None
  ingredients: str | None = None
  allergy_recommendations: str | None = None
  name_search_standard: str | None = None