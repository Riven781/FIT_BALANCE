from pydantic import BaseModel, Field

class ProductCategory(BaseModel):
  id: int
  name: str

class ProductBase(BaseModel):
  name: str
  brand: str | None
  kcal: float = Field(ge=0)
  reference_amount: int = Field(ge=0)
  reference_unit: str
  img_src: str
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
  reference_amount: int = Field(ge=0)
  reference_unit: str
  img_src: str
  category_id: int
  fat: float | None = None
  saturates: float | None = None
  carbohydrates: float | None = None
  sugars: float | None = None
  protein: float | None = None
  salt: float | None = None
  fiber: float | None = None
  ingredients: str | None = None
  allergy_recommendations: str | None = None


class ProductUpdate(BaseModel):
  id: int | None = None
  name: str | None = None
  brand: str | None = None
  kcal: float | None = Field(default=None, ge=0)
  reference_amount: int | None = None
  reference_unit: str | None = None
  img_src: str | None = None
  category: list[ProductCategory] | None = None
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


class PaginationMeta(BaseModel):
  page: int = Field(ge=1)
  limit: int = Field(ge=1)
  total: int = Field(ge=0)
  total_pages: int  = Field(ge=0)

class ProductListResponse(BaseModel):
  pagination: PaginationMeta
  data: list[ProductDetail | ProductSummary]

