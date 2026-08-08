
import aiosqlite
from product_catalog_context.domain.product import Product
from product_catalog_context.infrastructure.aiosqlite_repository.mapper import ProductMapper
from product_catalog_context.infrastructure.api.rest.dependencies.filters import ProductsFilters
from product_catalog_context.domain.enums.product_searching import NameMode, SortBy
from product_catalog_context.infrastructure.aiosqlite_repository.errors_mapper import map_errors
from product_catalog_context.infrastructure.aiosqlite_repository.repository import DbRepository


class ProductRepository(DbRepository):
  def __init__(self, db : aiosqlite.Connection):
    super().__init__(db, 'Product', mapper=ProductMapper)

    
  async def get_by_id(self, id) -> Product:
    get_query = """
      SELECT * FROM Product
      WHERE id = ?
    """
    try:
      async with self.db.execute(get_query, (id,)) as cursor:
        result = await cursor.fetchone()
    except Exception as e:
      raise map_errors(e) from e
    
    if result is None:
      return None
    result_dict = dict(result)

    return self.mapper.to_product(result_dict)

      