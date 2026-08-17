from product_catalog_context.infrastructure.aiosqlite_repository.errors_mapper import map_errors
from product_catalog_context.infrastructure.aiosqlite_repository.mapper import ProductCategoryHierarchyMapper
from product_catalog_context.infrastructure.aiosqlite_repository.repository import DbRepository


class ProductCategoryHierarchyRepository(DbRepository):
  def __init__(self, db, name='ProductCategoryHierarchy', mapper=ProductCategoryHierarchyMapper):
    super().__init__(db, name, mapper)

  async def get_by_id(self, hierarchy_id):
    get_hierarchy_query = """
      SELECT * FROM ProductCategoryHierarchy
      WHERE id = ?
    """

    get_categories_query = """
      SELECT * FROM ProductCategoryNode
      WHERE hierarchy_id = ?
    """

    async with self.db.execute(get_hierarchy_query, (hierarchy_id,)) as cursor:
      hierarchy = await cursor.fetchone()

    if hierarchy is None:
      return None

    hierarchy_dict = dict(hierarchy)

    async with self.db.execute(get_categories_query, (hierarchy_id,)) as cursor:
      categories = await cursor.fetchall()
    hierarchy_dict['categories'] = categories

    return self.mapper.to_hierarchy(hierarchy_dict)

  async def get_draft(self):
    get_hierarchy_query = """
      SELECT * FROM ProductCategoryHierarchy
      WHERE status = 'DRAFT' OR 'PLANNED_FOR_PUBLICATION'
    """

    get_categories_query = """
      SELECT * FROM ProductCategoryNode
      WHERE hierarchy_id = ?
    """

    async with self.db.execute(get_hierarchy_query) as cursor:
      hierarchy = await cursor.fetchone()
      
    if hierarchy is None:
      return None

    hierarchy_dict = dict(hierarchy)

    async with self.db.execute(get_categories_query, (hierarchy['id'],)) as cursor:
      categories = await cursor.fetchall()
      print(categories)
    hierarchy_dict['categories'] = categories

    return self.mapper.to_hierarchy(hierarchy_dict)

  async def get_planned_for_publication(self):
    get_hierarchy_query = """
      SELECT * FROM ProductCategoryHierarchy
      WHERE status = 'PLANNED_FOR_PUBLICATION'
    """

    get_categories_query = """
      SELECT * FROM ProductCategoryNode
      WHERE hierarchy_id = ?
    """

    async with self.db.execute(get_hierarchy_query) as cursor:
      hierarchy = await cursor.fetchone()
      
    if hierarchy is None:
      return None

    hierarchy_dict = dict(hierarchy)

    async with self.db.execute(get_categories_query, (hierarchy['id'],)) as cursor:
      categories = await cursor.fetchall()
      print(categories)
    hierarchy_dict['categories'] = categories

    return self.mapper.to_hierarchy(hierarchy_dict)  

  async def get_active(self):
    get_hierarchy_query = """
      SELECT * FROM ProductCategoryHierarchy
      WHERE status = 'ACTIVE'
    """

    get_categories_query = """
      SELECT * FROM ProductCategoryNode
      WHERE hierarchy_id = ?
    """

    async with self.db.execute(get_hierarchy_query) as cursor:
      hierarchy = await cursor.fetchone()
      
    if hierarchy is None:
      return None

    hierarchy_dict = dict(hierarchy)

    async with self.db.execute(get_categories_query, (hierarchy['id'],)) as cursor:
      categories = await cursor.fetchall()
    hierarchy_dict['categories'] = categories

    return self.mapper.to_hierarchy(hierarchy_dict)

  async def insert(self, hierarchy):
    hierarchy_dict : dict = self.mapper.to_storage_dict(hierarchy)
    categories = hierarchy_dict.pop('categories')
    insert_hierarchy_query = f"""
      INSERT INTO ProductCategoryHierarchy ({', '.join(hierarchy_dict.keys())})
      VALUES ({', '.join(['?' for _ in hierarchy_dict.values()])})
    """

    async with self.db.execute(insert_hierarchy_query, list(hierarchy_dict.values())) as cursor:
      hierarchy_id = cursor.lastrowid

    if not hierarchy.product_categories:
      return hierarchy_id

    row_placeholder = '(' + ', '.join(['?' for _ in categories[0].values()] + ['?']) + ')'
    value_placeholder = ', '.join(row_placeholder for _ in categories)
    
    insert_categories = f"""
      INSERT INTO ProductCategoryNode ({', '.join(categories[0].keys())}, hierarchy_id)
      VALUES {value_placeholder}
    """
    args = [list(category.values()) + [hierarchy_id]  for category in categories]
    args_flat = [value for arg in args for value in arg]
    async with self.db.execute(insert_categories, args_flat) as cursor:
      pass

    return hierarchy_id

  async def update(self, hierarchy_id, hierarchy):
    hierarchy_dict : dict = self.mapper.to_storage_dict(hierarchy)
    categories = hierarchy_dict.pop('categories')
    update_hierarchy_query = f"""
      UPDATE ProductCategoryHierarchy
      SET {', '.join([f'{key} = ?' for key in hierarchy_dict])}
      WHERE id = ?
    """

    args = [hierarchy_dict[key] for key in hierarchy_dict] + [hierarchy_id]
    async with self.db.execute(update_hierarchy_query, args) as cursor:
      count = cursor.rowcount

    if not categories or count == 0:
      return count

    get_categories_query = """
      SELECT * FROM ProductCategoryNode
      WHERE hierarchy_id = ?
    """
    category_ids = [category['id'] for category in categories]
    async with self.db.execute(get_categories_query, (hierarchy_id,)) as cursor:
      old_categories = await cursor.fetchall()
    old_category_ids = [category['id'] for category in old_categories]
    old_categories_by_id = {category['id'] : category for category in old_categories}
    ids_to_insert = [category['id'] for category in categories if category['id'] not in old_category_ids]

    if ids_to_insert:
      row_placeholder = '(' + ', '.join(['?' for _ in categories[0].values()] + ['?']) + ')'
      value_placeholder = ', '.join(row_placeholder for _ in ids_to_insert)
      insert_categories = f"""
        INSERT INTO ProductCategoryNode ({', '.join(categories[0].keys())}, hierarchy_id)
        VALUES {value_placeholder}
      """
      args = [list(category.values()) + [hierarchy_id]  for category in categories if category['id'] in ids_to_insert]
      args_flat = [value for arg in args for value in arg]

      async with self.db.execute(insert_categories, args_flat) as cursor:
        pass

    categories_to_update = [category for category in categories if category['id'] in old_category_ids and category != old_categories_by_id[category['id']]]
    if categories_to_update:
      update_categories_query = """
        UPDATE ProductCategoryNode 
        SET name = ?, parent_id=?
        WHERE id = ?
      """ 
      args = [list(category.values())  for category in categories_to_update]
      async with self.db.executemany(update_categories_query, args) as cursor:
        pass
      
    ids_to_delete = [old_category['id'] for old_category in old_categories if old_category['id'] not in category_ids]
    if ids_to_delete:
      placeholders = ', '.join('?' for _ in ids_to_delete)
      delete_query = f"""
      DELETE FROM ProductCategoryNode
      WHERE id IN ({placeholders})
      """
      print(delete_query)
      async with self.db.execute(delete_query, ids_to_delete) as cursor:
        pass
    return count

  async def delete(self, hierarchy_id):
    delete_hierarchy_query="""
      DELETE FROM ProductCategoryHierarchy
      WHERE id = ?
    """
    async with self.db.execute(delete_hierarchy_query, (hierarchy_id, )) as cursor:
      return cursor.rowcount

  async def delete_active(self):
    delete_hierarchy_query="""
      DELETE FROM ProductCategoryHierarchy
      WHERE status = 'ACTIVE'
    """
    async with self.db.execute(delete_hierarchy_query) as cursor:
      return cursor.rowcount

    

  async def rebuild_hierarchy(self,  hierarchy_id):
    delete_query = """
      DELETE FROM ProducCategoryClosure WHERE supercategory_id IN (
        SELECT node.id FROM ProductCategoryNode node
        JOIN ProductHierarchy hierarchy ON node.hierarchy_id = hierarchy.id
        WHERE hierarchy.id = ? AND hierarchy.status = 'ACTIVE'
      )
    """
    rebuild_query = """
    WITH RECURSIVE closure AS (
      SELECT id AS supercategory_id, id AS subcategory_id, 0 AS depth
      FROM ProductCategoryNode node
      JOIN ProductHierarchy hierarchy ON node.hierarchy_id = hierarchy.id
      WHERE hierarchy.id = ? AND hierarchy.status = 'ACTIVE'


      UNION ALL

      SELECT closure.supercategory_id, child.id, closure.depth + 1
      FROM closure
      JOIN ProductCategoryNode AS child
        ON child.parent_id = closure.subcategory_id
    )
    INSERT INTO ProductCategoryClosure (supercategory_id, subcategory_id, depth)
    SELECT supercategory_id, subcategory_id, depth FROM closure
    """
    await self.db.execute(delete_query, (hierarchy_id,))
    await self.db.execute(rebuild_query, (hierarchy_id,))


  async def next_category_id(self):
    update_id = """
    UPDATE IdSequence
    SET next_value = next_value + 1
    WHERE name = 'product_category'
    RETURNING next_value - 1 AS id
    """
    async with self.db.execute(update_id) as cursor:
      row = await cursor.fetchone()
    return row['id']

