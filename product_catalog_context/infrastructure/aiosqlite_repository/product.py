

import aiosqlite
from product_catalog_context.domain.product.product import Product
from product_catalog_context.infrastructure.aiosqlite_repository.mapper import ProductMapper
from product_catalog_context.infrastructure.api.rest.dependencies.filters import ProductsFilters
from product_catalog_context.domain.enums.product_searching import NameMode, SortBy
from product_catalog_context.infrastructure.aiosqlite_repository.errors_mapper import map_errors
from product_catalog_context.infrastructure.aiosqlite_repository.repository import DbRepository


class ProductRepository(DbRepository):
  def __init__(self, db : aiosqlite.Connection):
    super().__init__(db, 'Product', mapper=ProductMapper)

  async def get_without_planned_category_and_assignment_task(self, category_id, hierarchy_id, limit= 20):
    get_query = """
      SELECT product.*
      FROM Product product
      LEFT JOIN ProductCategoryAssignment a ON product.id = a.product_id
      WHERE
      a.node_id = ? 
      AND
      NOT EXISTS (
        SELECT 1 FROM ProductCategoryAssignment assignment 
        JOIN ProductCategoryNode node ON node.id = assignment.node_id
        JOIN ProductCategoryHierarchy hierarchy ON hierarchy.id = node.hierarchy_id
        WHERE assignment.product_id = product.id AND hierarchy.status = 'PLANNED_FOR_PUBLICATION'
      ) 
      AND  
      NOT EXISTS (SELECT 1 FROM ProductCategoryAssignmentTask WHERE hierarchy_id = ? AND product_id = product.id)
      LIMIT ?;
    """

    try:
      async with self.db.execute(get_query, (category_id, hierarchy_id, limit)) as cursor:
        result = await cursor.fetchall()
    except Exception as e:
      raise map_errors(e) from e
        
    if result is None:
      return None

    products = []
    for product in result:
      dict_product = dict(product)
      dict_product['category_assignments'] = {}
      products.append(dict_product)

    return [self.mapper.to_product(product)for product in products]

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
      SELECT product.*
      FROM Product product
      WHERE product.id = ?;
    """

    try:
      async with self.db.execute(get_query, (id,)) as cursor:
        result = await cursor.fetchone()
    except Exception as e:
      raise map_errors(e) from e
        
    if result is None:
      return None
    
    result_dict = dict(result)

    get_assignments_query = """
      SELECT node.hierarchy_id, assignment.node_id FROM ProductCategoryAssignment assignment
      JOIN ProductCategoryNode node ON node.id = assignment.node_id
      WHERE assignment.product_id = ?
    """
    async with self.db.execute(get_assignments_query, (id,)) as cursor:
      assignments = await cursor.fetchall()

    category_assignments = {assignment['hierarchy_id'] : assignment['node_id'] for assignment in assignments}
    
    result_dict['category_assignments'] = category_assignments

    return self.mapper.to_product(result_dict)

  async def insert(self, obj : Product, **options):
    product_dict : dict = self.mapper.to_storage_dict(obj)
    category_assignments = product_dict.pop('category_assignments')

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
    
    category_nodes = list(category_assignments.values())
    if category_nodes:
      placeholder = '.'.join(['(? , ?)' for _ in category_nodes])
      insert_query = f"""
        INSERT INTO ProductCategoryAssignment (product_id, node_id)
        VALUES {placeholder}
      """
      args = []
      for node in category_nodes:
        args.extend([product_id, node])
      try:
        async with self.db.execute(insert_query, args) as cursor:
          pass
      except Exception as e:
        raise map_errors(e) from e

    return product_id

  async def update(self, product_id, obj : Product, **options):
    product_dict : dict = self.mapper.to_storage_dict(obj)
    category_assignments = product_dict.pop('category_assignments')

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

    category_nodes = list(category_assignments.values())

    try:
      if not category_nodes:
        delete_all_assignments_query = """
          DELETE FROM ProductCategoryAssignment
          WHERE product_id = ?
        """
        async with self.db.execute(delete_all_assignments_query, (product_id, )) as cursor:
          pass
      else:
        placeholder = ', '.join(['?' for _ in category_nodes])
        delete_assignments_query = f"""
          DELETE FROM ProductCategoryAssignment
          WHERE product_id = ? AND node_id NOT IN ({placeholder})
        """
        async with self.db.execute(delete_assignments_query, (product_id, *category_nodes)) as cursor:
          pass
        placeholder = ','.join(['(? , ?)' for _ in category_nodes])
        insert_query = f"""
        INSERT INTO ProductCategoryAssignment (product_id, node_id)
        VALUES {placeholder}
        ON CONFLICT (product_id, node_id) DO NOTHING
        """
        args = []
        for node in category_nodes:
          args.extend([product_id, node])
        async with self.db.execute(insert_query, args) as cursor:
          pass
    except Exception as e:
      raise map_errors(e) from e
    
    return count  



  async def copy_category_assignments(self, active_hierarchy_id, draft_hierarchy_id):
    insert_assignments = """
      INSERT INTO ProductCategoryAssignment (product_id, node_id)
      SELECT assignment.product_id, draft_node.id FROM ProductCategoryAssignment assignment
      JOIN ProductCategoryNode active_node ON active_node.id = assignment.node_id
      JOIN ProductCategoryNode draft_node ON active_node.id = draft_node.source_node_id
      WHERE active_node.hierarchy_id = ? AND draft_node.hierarchy_id = ?
    """
    await self.db.execute(insert_assignments, (active_hierarchy_id, draft_hierarchy_id))

  async def delete_category_assignments_by_category_id(self, category_ids):
    placeholder = ', '.join(['?' for _ in category_ids])
    delete_assignments = f"""
      DELETE FROM ProductCategoryAssignment
      WHERE node_id IN ({placeholder})
    """
    
    print(delete_assignments)
    await self.db.execute(delete_assignments, category_ids)