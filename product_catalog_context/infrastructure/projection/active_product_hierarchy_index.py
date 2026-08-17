
class ActiveProductHierarchyIndex:
  def __init__(self, db,):
    self.db = db

  async def rebuild_hierarchy(self,  hierarchy_id):
    delete_query = """
      DELETE FROM ProducCategoryClosure;
    """
    rebuild_query = """
    WITH RECURSIVE closure AS (
      SELECT id AS supercategory_id, id AS subcategory_id, 0 AS depth
      FROM ProductCategoryNode node
      JOIN ProductHierarchy hierarchy ON node.hierarchy_id = hierarchy.id
      WHERE hierarchy.id = ?

      UNION ALL

      SELECT closure.supercategory_id, child.id, closure.depth + 1
      FROM closure
      JOIN ProductCategoryNode AS child
        ON child.parent_id = closure.subcategory_id
    )
    INSERT INTO ProductCategoryClosure (supercategory_id, subcategory_id, depth)
    SELECT supercategory_id, subcategory_id, depth FROM closure
    """
    await self.db.execute(delete_query)
    await self.db.execute(rebuild_query, (hierarchy_id,))
