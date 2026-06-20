import aiosqlite
from api.repository.aiosqlite.errors_mapper import map_errors
from api.repository.aiosqlite.repository import DbRepository
from api.schemas.product_category import ProductCategoryHierarchy

class ProductCategoryRepository(DbRepository):
  def __init__(self, db, name='ProductCategory'):
    super().__init__(db, name)

  async def get_by_supercategory(self, supercategory_id) -> ProductCategoryHierarchy | None:
    get_by_supertype_query = f"""
      SELECT * FROM ProductCategory AS pc
      JOIN ProductCategoryClosure AS pcc ON pc.id  = pcc.subcategory_id
      WHERE pcc.supercategory_id = ?
      ORDER BY pcc.depth
    """
    try:
      async with self.db.execute(get_by_supertype_query, [supercategory_id]) as cursor:
        results = await cursor.fetchall()
    except Exception as e:
      raise map_errors(e) from e
    
    if not results:
      return None
    
    external_categories_by_id = {}
    all_categories_by_id = {}
    for row in results:
      row_dict = dict(row)
      category_id = row_dict['id']
      all_categories_by_id[category_id] = {"id": category_id, "name": row_dict['name'], 'subcategories': []}
      if row_dict['depth'] == 0:
        external_categories_by_id[category_id] = all_categories_by_id[category_id]
      else:
        parent_id = row_dict['parent_id']
        all_categories_by_id[parent_id]['subcategories'].append(all_categories_by_id[category_id])

    root_hierarchy = list(external_categories_by_id.values())[0]
  
    
    return ProductCategoryHierarchy(**root_hierarchy)
