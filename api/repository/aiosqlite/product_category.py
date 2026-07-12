import aiosqlite
from httpx import delete
from api.repository.aiosqlite.errors_mapper import map_errors
from api.repository.aiosqlite.repository import DbRepository
from api.schemas.product_category import ProductCategoryCreate, ProductCategoryHierarchy, ProductCategoryUpdate

class ProductCategoryRepository(DbRepository):
  def __init__(self, db, name='ProductCategory'):
    super().__init__(db, name)

  async def get_all(self):
    get_all_query  = """
    SELECT id, name, parent_id
    FROM ProductCategory
    """
    try:
      async with self.db.execute(get_all_query) as cursor:
        data = await cursor.fetchall()
    except Exception as e:
      map_errors(e)
    categories = [dict(row) for row in data]
    return categories






