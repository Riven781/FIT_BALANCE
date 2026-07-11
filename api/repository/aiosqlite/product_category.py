import aiosqlite
from httpx import delete
from api.repository.aiosqlite.errors_mapper import map_errors
from api.repository.aiosqlite.repository import DbRepository
from api.schemas.product_category import ProductCategoryCreate, ProductCategoryHierarchy, ProductCategoryUpdate

class ProductCategoryRepository(DbRepository):
  def __init__(self, db, name='ProductCategory'):
    super().__init__(db, name)





