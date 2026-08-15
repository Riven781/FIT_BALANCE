import sqlite3

from product_catalog_context.application.query.active_category_hierarchy import ActiveCategoryHierarchy, CategoryHierarchyNode
from product_catalog_context.domain.product_category import ProductCategoryNode
from product_catalog_context.infrastructure.aiosqlite_repository.errors_mapper import map_errors


class ProductCategoryHierarchyQueries:
  def __init__(self, db: sqlite3.Connection):
    self.db = db

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
  
  async def get(self) -> ActiveCategoryHierarchy:
    get_all_query =  """
        SELECT child.*, pcc.* FROM ProductCategoryClosure AS pcc
        JOIN ProductCategoryNode AS root ON root.id  = pcc.supercategory_id
        JOIN ProductCategoryNode AS child ON child.id = pcc.subcategory_id
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
    hierarchy_list = [CategoryHierarchyNode(**hierarchy_tree) for hierarchy_tree in hierarchy_dict.values()]
    return hierarchy_list

  async def get_by_supercategory(self, supercategory_id) -> CategoryHierarchyNode | None:
    get_by_supertype_query = """
      SELECT * FROM ProductCategoryNode AS node
      JOIN ProductCategoryClosure AS pcc ON node.id  = pcc.subcategory_id
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
  
    return CategoryHierarchyNode(**root_hierarchy)  