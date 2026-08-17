
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

  async def get_without_planned_category_and_task(self, category_id, hierarchy_id, limit= 20):
    get_query = """
      SELECT product.*,
      MAX(
        CASE 
          WHEN hierarchy.status = 'ACTIVE'
          THEN node.id
        END
      )AS current_category_id,
      MAX(
        CASE 
          WHEN hierarchy.status = 'DRAFT'
          THEN node.id
        END
      ) AS planned_category_id
      FROM Product product
      LEFT JOIN ProductCategoryAssignment assignment ON assignment.product_id = product.id 
      LEFT JOIN ProductCategoryNode node ON node.id = assignment.node_id
      LEFT JOIN ProductCategoryHierarchy hierarchy ON hierarchy.id = node.hierarchy_id
      GROUP BY product.id
      HAVING current_category_id = ? AND planned_category_id IS NULL AND NOT EXISTS (SELECT 1 FROM ProductCategoryAssignmentTask WHERE hierarchy_id = ? AND product_id = product.id)
      LIMIT ?;
    """

    try:
      async with self.db.execute(get_query, (category_id, hierarchy_id, limit)) as cursor:
        result = await cursor.fetchall()
    except Exception as e:
      raise map_errors(e) from e
        
    if result is None:
      return None

    
    return [self.mapper.to_product(dict(product))for product in result]

  async def get_total_without_planned_category(self):
    get_total_query = """
    SELECT COUNT(*) AS total_without_planned_category FROM Product product
    WHERE NOT EXISTS (
      SELECT 1
      FROM ProductCategoryAssignment assignment
      JOIN ProductCategoryNode node ON node.id = assignment.node_id
      JOIN ProductCategoryHierarchy hierarchy ON hierarchy.id = node.hierarchy_id
      WHERE assignment.product_id = product.id AND hierarchy.status IN ('DRAFT', 'PLANNED_FOR_PUBLICATION')
    ) 
    """
    async with self.db.execute(get_total_query) as cursor:
      result = await cursor.fetchone()
    return result['total_without_planned_category']


  async def get_by_id(self, id):
    get_query = """
      SELECT product.*,
      MAX(
        CASE 
          WHEN hierarchy.status = 'ACTIVE'
          THEN node.id
        END
      )AS current_category_id,
      MAX(
        CASE 
          WHEN hierarchy.status = 'PLANNED_FOR_PUBLICATION'
          THEN node.id
        END
      ) AS planned_category_id
      FROM Product product
      LEFT JOIN ProductCategoryAssignment assignment ON assignment.product_id = product.id 
      LEFT JOIN ProductCategoryNode node ON node.id = assignment.node_id
      LEFT JOIN ProductCategoryHierarchy hierarchy ON hierarchy.id = node.hierarchy_id
      WHERE product.id = ?
      GROUP BY product.id;
    """

    try:
      async with self.db.execute(get_query, (id,)) as cursor:
        result = await cursor.fetchone()
    except Exception as e:
      raise map_errors(e) from e
        
    if result is None:
      return None
    result_dict = dict(result)
    print(result_dict)
    return self.mapper.to_product(result_dict)

  async def insert(self, obj : Product, **options):
    product_dict : dict = self.mapper.to_storage_dict(obj)
    current_category_id = product_dict.pop('current_category_id')
    planned_category_id = product_dict.pop('planned_category_id')

    keys = ", ".join(product_dict.keys()) 
    vals = ', '.join(['?' for _ in product_dict.values()]) 

    insert_product_query = f"""
    INSERT INTO Product ({keys}) VALUES ({vals})
    """

    try:
      async with self.db.execute(insert_product_query, list(product_dict.values())) as cursor:
        product_id = cursor.lastrowid 
    except Exception as e:
      raise map_errors(e) from e

    if current_category_id:
      insert_category_assigment = """
        INSERT INTO ProductCategoryAssignment (product_id, node_id)
        VALUES (?, ?)
      """

      try:
        async with self.db.execute(insert_category_assigment, (product_id, current_category_id)) as cursor:
          pass
      except Exception as e:
        raise map_errors(e) from e

    if planned_category_id:
      insert_category_assigment = """
        INSERT INTO (product_id, node_id) ProductCategoryAssignment
        VALUES (?, ?)
      """
      try:
        async with self.db.execute(insert_category_assigment, (product_id, planned_category_id)) as cursor:
          pass
      except Exception as e:
        raise map_errors(e) from e

    return product_id

  async def update(self, product_id, obj : Product, **options):
    product_dict : dict = self.mapper.to_storage_dict(obj)
    new_current_category_id = product_dict.pop('current_category_id')
    new_planned_category_id = product_dict.pop('planned_category_id')


    set = ', '.join([f'{column} = ?' for column in product_dict.keys()]) 

    vals =  list(product_dict.values())
    vals.append(product_id)

    update_product_query = f"""
      UPDATE Product
      SET  {set}
      WHERE id = ?
      RETURNING id;
    """

    try:
      async with self.db.execute(update_product_query, vals) as cursor:
        count = cursor.rowcount 
        row = await cursor.fetchone()

    except Exception as e:
      raise map_errors(e) from e


    if row is None:
        return 0
    

    await self._sync_category_assignment(product_id, 'ACTIVE', new_current_category_id)
    await self._sync_category_assignment(product_id, 'DRAFT', new_planned_category_id)


    return count  


  async def _sync_category_assignment(self, product_id, status, new_node_id):
    get_assignment = """
      SELECT assignment.node_id AS node_id FROM ProductCategoryAssignment assignment
      JOIN ProductCategoryNode node ON node.id = assignment.node_id
      JOIN ProductCategoryHierarchy hierarchy ON node.hierarchy_id = hierarchy.id
      WHERE assignment.product_id = ? AND hierarchy.status = ?
    """
    async with self.db.execute(get_assignment, (product_id, status)) as cursor:
      row = await cursor.fetchone()
    current_node_id = row["node_id"] if row else None
    if current_node_id is None and new_node_id is None:
      return

    if current_node_id is None:
      insert_category_assignment = """
        INSERT INTO ProductCategoryAssignment (product_id, node_id) 
        VALUES (?, ?)
      """
      try:
        async with self.db.execute(insert_category_assignment, (product_id, new_node_id)) as cursor:
          pass
      except Exception as e:
        raise map_errors(e) from e 
      return

    if new_node_id is None:
      delete_category_assignment = """
        DELETE FROM ProductCategoryAssignment
        WHERE product_id = ? AND node_id = ?
      """    
      try:
        async with self.db.execute(delete_category_assignment, (product_id, current_node_id)) as cursor:
          pass
      except Exception as e:
        raise map_errors(e) from e 
      return
    if new_node_id != current_node_id:
      update_category_assignment = """
        UPDATE ProductCategoryAssignment
        SET node_id = ?,
            assigned_at = CURRENT_TIMESTAMP
        WHERE product_id = ? AND node_id = ?
      """
      try:
        async with self.db.execute(update_category_assignment, (new_node_id, product_id, current_node_id)) as cursor:
          pass
      except Exception as e:
        raise map_errors(e) from e 

  async def copy_category_assignments(self, active_hierarchy_id, draft_hierarchy_id):
    insert_assignments = """
      INSERT INTO ProductCategoryAssignment (product_id, node_id)
      SELECT assignment.product_id, draft_node.id FROM ProductCategoryAssignment assignment
      JOIN ProductCategoryNode active_node ON active_node.id = assignment.node_id
      JOIN ProductCategoryNode draft_node ON active_node.id = draft_node.source_node_id
      WHERE active_node.hierarchy_id = ? AND draft_node.hierarchy_id = ?
    """
    await self.db.execute(insert_assignments, (active_hierarchy_id, draft_hierarchy_id))

  async def delete_category_assignments(self, category_ids):
    placeholder = ', '.join(['?' for _ in category_ids])
    delete_assignments = f"""
      DELETE FROM ProductCategoryAssignment
      WHERE node_id IN ({placeholder})
    """
    
    print(delete_assignments)
    await self.db.execute(delete_assignments, category_ids)