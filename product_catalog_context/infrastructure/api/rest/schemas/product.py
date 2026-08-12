from dataclasses import field

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from product_catalog_context.application.command.product import ProductCommand
from product_catalog_context.infrastructure.api.rest.schemas.product_category import ProductCategory, ProductCategoryItem
from product_catalog_context.domain.nutrition_facts import NutritionFacts as domain_NutritionFacts, ReferenceQuantity as domain_ReferenceQuantity, Nutrients as domain_Nutrients

class PartialNutrients(BaseModel):
  model_config = ConfigDict(frozen=True, from_attributes=True)
  fat: float | None = None
  saturates: float | None = None
  carbohydrates: float | None = None
  sugars: float | None = None
  protein: float | None = None
  salt: float | None = None
  fiber: float | None = None

class DefaultReferenceQuantity(BaseModel):
  model_config = ConfigDict(frozen=True, from_attributes=True)
  amount: int = 100
  unit: str ='g'

class DefaultNutritionFacts(BaseModel):
  model_config = ConfigDict(frozen=True, from_attributes=True)
  reference_quantity : DefaultReferenceQuantity = Field(default_factory=DefaultReferenceQuantity)
  kcal : int = Field(ge=0)
  nutrients : PartialNutrients = Field(default_factory=PartialNutrients)

class ProductPostRequest(BaseModel):
  model_config = ConfigDict(frozen=True, extra='forbid')
  name: str
  brand_name: str
  nutrition_facts: DefaultNutritionFacts
  img_src: str | None
  current_category_id: int | None = None
  planned_category_id: int | None = None
  ingredients: str | None = None
  allergy_recommendations : str | None = None

  def to_command(self):
    reference_quantity = domain_ReferenceQuantity(
      amount=self.nutrition_facts.reference_quantity.amount,
      unit=self.nutrition_facts.reference_quantity.unit)
    nutrients = domain_Nutrients(
      **self.nutrition_facts.nutrients.model_dump()
    )
    nutrition_facts = domain_NutritionFacts(kcal=self.nutrition_facts.kcal, reference_quantity=reference_quantity, nutrients=nutrients)
    return ProductCommand(
      name=self.name,
      brand_name=self.brand_name,
      nutrition_facts=nutrition_facts,
      img_src=self.img_src,
      current_category_id=self.current_category_id,
      planned_category_id=self.planned_category_id,
      ingredients=self.ingredients,
      allergy_recommendations=self.allergy_recommendations
    )  

class Nutrients(BaseModel):
  model_config = ConfigDict(frozen=True, from_attributes=True)
  fat: float | None
  saturates: float | None
  carbohydrates: float | None
  sugars: float | None
  protein: float | None
  salt: float | None
  fiber: float | None

class ReferenceQuantity(BaseModel):
  model_config = ConfigDict(frozen=True, from_attributes=True)
  amount: int
  unit: str

class NutritionFacts(BaseModel):
  model_config = ConfigDict(frozen=True, from_attributes=True)
  reference_quantity : ReferenceQuantity
  kcal : int = Field(ge=0)
  nutrients : Nutrients

class ProductResponse(BaseModel):
  model_config = ConfigDict(frozen=True, from_attributes=True)
  product_id: int
  name: str
  brand_name: str
  nutrition_facts: NutritionFacts
  img_src: str | None
  current_category_id: int | None
  planned_category_id: int | None

class ProductPutRequest(BaseModel):
  model_config = ConfigDict(frozen=True, extra='forbid')
  name: str
  brand_name: str
  nutrition_facts: NutritionFacts
  img_src: str | None
  ingredients: str | None
  allergy_recommendations : str | None
  current_category_id: int | None
  planned_category_id: int | None

  def to_command(self):
    reference_quantity = domain_ReferenceQuantity(
      amount=self.nutrition_facts.reference_quantity.amount,
      unit=self.nutrition_facts.reference_quantity.unit)
    nutrients = domain_Nutrients(
      **self.nutrition_facts.nutrients.model_dump()
    )
    nutrition_facts = domain_NutritionFacts(kcal=self.nutrition_facts.kcal, reference_quantity=reference_quantity, nutrients=nutrients)
    return ProductCommand(
      name=self.name,
      brand_name=self.brand_name,
      nutrition_facts=nutrition_facts,
      img_src=self.img_src,
      current_category_id=self.current_category_id,
      planned_category_id=self.planned_category_id,
      ingredients=self.ingredients,
      allergy_recommendations=self.allergy_recommendations
    )  

class PublicProductResponse(BaseModel):
  model_config = ConfigDict(frozen=True, from_attributes=True)
  product_id: int
  name: str
  brand_name: str
  nutrition_facts: NutritionFacts
  img_src: str | None
  category_path: list[ProductCategoryItem]

class PaginationMeta(BaseModel):
  page: int = Field(ge=1)
  limit: int = Field(ge=1)
  total: int = Field(ge=0)
  total_pages: int  = Field(ge=0)

class PublicProductListResponse(BaseModel):
  pagination: PaginationMeta
  data: list[PublicProductResponse]

class ProductListResponse(BaseModel):
  pagination: PaginationMeta
  data: list[ProductResponse]

"""
class ProductBase(BaseModel):
  model_config = ConfigDict(frozen=True)
  name: str
  brand_name: str | None
  nutrition_facts : "NutritionFacts"
  img_src: str | None = None
  category: list[ProductCategoryView]

class ProductSummary(ProductBase):
  id: int

class Nutrients(BaseModel):
  fat: float | None = None
  saturates: float | None = None
  carbohydrates: float | None = None
  sugars: float | None = None
  protein: float | None = None
  salt: float | None = None
  fiber: float | None = None
  ingredients: str | None = None

class ReferenceQuantity(BaseModel):
  amount: int
  unit: str

class NutritionFacts(BaseModel):
  reference_quantity : ReferenceQuantity
  kcal : int = Field(ge=0)
  nutrients : Nutrients


class ProductDetail(ProductBase):
  id: int
  ingredients: str | None = None
  allergy_recommendations: str | None = None

class ProductCreate(BaseModel):
  model_config = {"extra" : "forbid"}
  name: str
  brand: str | None
  img_src: str | None = None
  category_id: int | None = None
  ingredients: str | None = None
  allergy_recommendations: str | None = None
  #name_search_standard: str | None = None

class ProductModel(BaseModel):
  id: int | None = None
  name: str | None = None
  brand: str | None = None
  kcal: float | None = Field(default=None, ge=0)
  reference_amount: int | None = None
  reference_unit: str | None = None
  img_src: str | None = None
  fat: float | None = None
  saturates: float | None = None
  carbohydrates: float | None = None
  sugars: float | None = None
  protein: float | None = None
  salt: float | None = None
  fiber: float | None = None
  ingredients: str | None = None
  allergy_recommendations: str | None = None
  category_id: int | None = None
  name_search_standard: str | None = None

class ProductUpdate(BaseModel):
  model_config = {"extra" : "forbid"}
  id: int | None = None
  name: str | None = None
  brand: str | None = None
  kcal: float | None = Field(default=None, ge=0)
  reference_amount: int | None = None
  reference_unit: str | None = None
  img_src: str | None = None
  fat: float | None = None
  saturates: float | None = None
  carbohydrates: float | None = None
  sugars: float | None = None
  protein: float | None = None
  salt: float | None = None
  fiber: float | None = None
  ingredients: str | None = None
  allergy_recommendations: str | None = None
  category_id: int | None = None
  #name_search_standard: str | None = None
  @model_validator(mode='after')
  def not_null_fields(self):
    if len(self.model_fields_set) == 0:
      raise ValueError(f'body cannot be empty')
    fields_that_cannot_be_null = {'name', 'kcal', 'reference_unit'}
    for field in fields_that_cannot_be_null:
      if field in self.model_fields_set and getattr(self, field) is None:
        raise ValueError(f"{field} cannot be null")
    return self
    



class PaginationMeta(BaseModel):
  page: int = Field(ge=1)
  limit: int = Field(ge=1)
  total: int = Field(ge=0)
  total_pages: int  = Field(ge=0)

class ProductListResponse(BaseModel):
  pagination: PaginationMeta
  data: list[ProductDetail | ProductSummary]


"""

