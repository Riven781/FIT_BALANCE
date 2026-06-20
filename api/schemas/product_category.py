from pydantic import BaseModel, ConfigDict, model_validator


class ProductCategory(BaseModel):
  id: int
  name: str


class ProductCategoryCreate(BaseModel):
  name: str
  supercategory_id: int | None
  subcategory_id: int | None

class ProductCategoryUpdate(BaseModel):
  model_config = ConfigDict(extra='forbid')
  name: str | None
  supercategory_id: int | None
  subcategory_id: int | None

  @model_validator(mode='after')
  def not_null_name(self):
    if len(self.model_fields_set) == 0:
      raise ValueError('body cannot be empty')
    if 'name' in self.model_fields_set and getattr(self, 'name') is None:
      raise ValueError('name cannot be null')



class ProductCategoryHierarchy(BaseModel):
  id: int
  name: str
  subcategories: list["ProductCategoryHierarchy"]