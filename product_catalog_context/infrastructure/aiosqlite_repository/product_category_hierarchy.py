from product_catalog_context.infrastructure.aiosqlite_repository.errors_mapper import map_errors
from product_catalog_context.infrastructure.aiosqlite_repository.repository import DbRepository
from product_catalog_context.infrastructure.api.rest.schemas.product_category import ProductCategoryHierarchy


class ProductCategoryHierarchyRepository(DbRepository):
  def __init__(self, db, name='ProductCategoryClosure'):
    super().__init__(db, name)

  async def rebuild_hierarchy(self):
    rebuil_query = """
    WITH RECURSIVE closure AS (
      SELECT id AS supercategory_id, id AS subcategory_id, 0 AS depth
      FROM ProductCategory

      UNION ALL

      SELECT closure.supercategory_id, child.id, closure.depth + 1
      FROM closure
      JOIN ProductCategory AS child
        ON child.parent_id = closure.subcategory_id
    )
    INSERT INTO ProductCategoryClosure (supercategory_id, subcategory_id, depth)
    SELECT supercategory_id, subcategory_id, depth FROM closure
    """
    await self.db.execute("DELETE FROM ProducCategoryClosure")
    await self.db.execute(rebuil_query)



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


  async def get(self) -> list[ProductCategoryHierarchy]:
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
      
    if not rows:
      return []
      
    hierarchy_dict = self._format_category_hierarchy(rows)

    hierarchy_list = [ProductCategoryHierarchy(**hierarchy_tree) for hierarchy_tree in hierarchy_dict.values()]
    return hierarchy_list
  
  
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