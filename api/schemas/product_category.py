from pydantic import BaseModel, ConfigDict, model_validator


class ProductCategory(BaseModel):
  id: int
  name: str
  parent_id: int | None

class ProductCategoryView(BaseModel):
  id: int
  name: str

class ProductCategoryCreate(BaseModel):
  model_config = ConfigDict(extra='ignore')
  name: str
  parent_id: int | None

 

class ProductCategoryUpdate(BaseModel):
  model_config = ConfigDict(extra='ignore')
  name: str | None = None
  parent_id: int | None = None

  @model_validator(mode='after')
  def not_null_name(self):
    if len(self.model_fields_set) == 0:
      raise ValueError('body cannot be empty')
    if 'name' in self.model_fields_set and getattr(self, 'name') is None:
      raise ValueError('name cannot be null')
    return self



class ProductCategoryHierarchy(BaseModel):
  id: int
  name: str
  subcategories: list["ProductCategoryHierarchy"]