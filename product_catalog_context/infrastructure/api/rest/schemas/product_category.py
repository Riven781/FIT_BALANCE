from dataclasses import asdict

from pydantic import BaseModel, ConfigDict, model_validator

from product_catalog_context.application.command.category_hierarchy import ProductCategoryDTO, ProductCategoryDraftDTO
from product_catalog_context.domain.category_hierarchy.product_category_hierarchy_status import ProductCategoryHierarchyStatus

class ProductCategoryItem(BaseModel):
  category_id: int
  name: str

class ProductCategory(BaseModel):
  model_config = ConfigDict(from_attributes=True)
  category_id: int
  name: str
  parent_id: int | None
  source_node_id: int| None

class ProductCategoryDraft(BaseModel):
  model_config = ConfigDict(from_attributes=True)
  name: str
  parent_id: int | None
  temp_id: int | str

class ProductCategoryHierarchyResponse(BaseModel):
  hierarchy_id: int
  product_categories: list[ProductCategory]
  status: ProductCategoryHierarchyStatus
  created_by: int | None
  published_by: int | None

class EditProductCategoryHierarchyRequest(BaseModel):
  model_config = ConfigDict(from_attributes=True)
  existing_categories: list[ProductCategory]
  draft_categories: list[ProductCategoryDraft]

  @property
  def existing_categories(self):
    return [ProductCategoryDTO(**asdict(existing_category)) for existing_category in self.existing_categories]

  @property
  def draft_categories(self):
    return [ProductCategoryDraftDTO(**asdict(draft_category)) for draft_category in self.draft_categories]

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



class ProductCategoryHierarchyNode(BaseModel):
  id: int
  name: str
  subcategories: list["ProductCategoryHierarchyNode"]