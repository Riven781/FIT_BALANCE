from pydantic import BaseModel, ConfigDict, Field, model_validator

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
  """
  @model_validator(mode="after")
  def at_least_one_field(self):
    if not self.model_fields_set:
      raise ValueError("At least one field must be provided")
    return self
  """


class PaginationMeta(BaseModel):
  page: int = Field(ge=1)
  limit: int = Field(ge=1)
  total: int = Field(ge=0)
  total_pages: int  = Field(ge=0)

class ProductListResponse(BaseModel):
  pagination: PaginationMeta
  data: list[ProductDetail | ProductSummary]

