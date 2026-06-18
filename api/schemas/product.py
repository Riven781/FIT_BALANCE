from dataclasses import field

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

class ProductCategory(BaseModel):
  id: int
  name: str

class ProductBase(BaseModel):
  model_config = ConfigDict(frozen=True)

  name: str
  brand: str | None
  kcal: float = Field(ge=0)
  reference_amount: int = Field(ge=0)
  reference_unit: str
  img_src: str | None = None
  category: list[ProductCategory]

class ProductSummary(ProductBase):
  id: int

class ProductDetail(ProductBase):
  id: int
  fat: float | None = None
  saturates: float | None = None
  carbohydrates: float | None = None
  sugars: float | None = None
  protein: float | None = None
  salt: float | None = None
  fiber: float | None = None
  ingredients: str | None = None
  allergy_recommendations: str | None = None

class ProductCreate(BaseModel):
  model_config = {"extra" : "forbid"}
  name: str
  brand: str | None
  kcal: float = Field(ge=0)
  reference_amount: int = Field(ge=0, default=100)
  reference_unit: str
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

