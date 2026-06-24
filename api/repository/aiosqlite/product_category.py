import aiosqlite
from api.repository.aiosqlite.errors_mapper import map_errors
from api.repository.aiosqlite.repository import DbRepository
from api.schemas.product_category import ProductCategoryHierarchy

class ProductCategoryRepository(DbRepository):
  def __init__(self, db, name='ProductCategory'):
    super().__init__(db, name)

  def _format_category_hierarchy(self, rows):
    external_categories_by_id = {}
    all_categories_by_id = {}
    for row in rows:
      row_dict = dict(row)
      category_id = row_dict['id']
      all_categories_by_id[category_id] = {"id": category_id, "name": row_dict['name'], 'subcategories': []}
      if row_dict['depth'] == 0:
        external_categories_by_id[category_id] = all_categories_by_id[category_id]
      else:
        parent_id = row_dict['parent_id']
        all_categories_by_id[parent_id]['subcategories'].append(all_categories_by_id[category_id])
    return external_categories_by_id

  async def get_by_supercategory(self, supercategory_id) -> ProductCategoryHierarchy | None:
    get_by_supertype_query = """
      SELECT * FROM ProductCategory AS pc
      JOIN ProductCategoryClosure AS pcc ON pc.id  = pcc.subcategory_id
      WHERE pcc.supercategory_id = ?
      ORDER BY pcc.depth
    """
    try:
      async with self.db.execute(get_by_supertype_query, [supercategory_id]) as cursor:
        rows = await cursor.fetchall()
    except Exception as e:
      raise map_errors(e) from e
    
    if not rows:
      return None
    
    hierarchy_dict = self._format_category_hierarchy(rows)
    root_hierarchy = list(hierarchy_dict.values())[0]
  
    return ProductCategoryHierarchy(**root_hierarchy)
  
  async def get_all(self) -> list[ProductCategoryHierarchy]:
    get_all_query =  """
      SELECT child.*, pcc.* FROM ProductCategoryClosure AS pcc
      JOIN ProductCategory AS root ON root.id  = pcc.supercategory_id
      JOIN ProductCategory AS child ON child.id = pcc.subcategory_id
      WHERE root.parent_id IS NULL
      ORDER BY pcc.depth
    """
    try:
      async with self.db.execute(get_all_query) as cursor:
        rows = await cursor.fetchall()
    except Exception as e:
      raise map_errors(e) from e
    #print([dict(r) for r in rows])
    
    if not rows:
      return []
    
    hierarchy_dict = self._format_category_hierarchy(rows)

    hierarchy_list = [ProductCategoryHierarchy(**hierarchy_tree) for hierarchy_tree in hierarchy_dict.values()]
    return hierarchy_list