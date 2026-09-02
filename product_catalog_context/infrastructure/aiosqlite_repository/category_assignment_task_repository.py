from product_catalog_context.domain.category_assignment_task import CategoryAssignmentTask
from product_catalog_context.infrastructure.aiosqlite_repository.mapper import CategoryAssignmentTaskMapper
from product_catalog_context.infrastructure.aiosqlite_repository.repository import DbRepository


class CategoryAssignmentTaskRepository(DbRepository):
  def __init__(self, db, name='ProductCategoryAssignmentTask', mapper=CategoryAssignmentTaskMapper):
    super().__init__(db, name, mapper)

  async def get_by_id(self, task_id) -> CategoryAssignmentTask:
    get_task = """
    SELECT * FROM ProductCategoryAssignmentTask WHERE id = ?
    """
    async with self.db.execute(get_task, (task_id,)) as cursor:
      task = await cursor.fetchone()


    if task is None:
      return None

    return self.mapper.to_task(task)

  async def get_by_product_and_hierarchy(self, product_id, hierarchy_id) -> CategoryAssignmentTask:
    get_task = """
    SELECT * FROM ProductCategoryAssignmentTask WHERE product_id = ? AND hierarchy_id = ?
    """
    async with self.db.execute(get_task, (product_id, hierarchy_id)) as cursor:
      task = await cursor.fetchone()

    if task is None:
      return None

    return self.mapper.to_task(task)

  async def insert_tasks_for_unassigned_products(self, user_id, hierarchy_id, limit):
    insert_query = """
    INSERT INTO ProductCategoryAssignmentTask (product_id, hierarchy_id, user_id, status)
    SELECT product.id, ?, ?, 'PENDING' FROM Product product
    WHERE NOT EXISTS (
      SELECT 1 FROM ProductCategoryAssignmentTask task
      WHERE task.product_id = product.id AND task.hierarchy_id = ?
    ) AND NOT EXISTS (
      SELECT 1 FROM ProductCategoryAssignment assignment
      JOIN ProductCategoryNode node ON node.id = assignment.node_id
      WHERE assignment.product_id = product.id AND node.hierarchy_id = ?
    )
    ORDER BY product.id
    LIMIT ?
    """
    async with self.db.execute(insert_query, (hierarchy_id, user_id, hierarchy_id, hierarchy_id, limit)) as cursor:
      return cursor.rowcount

  async def delete_by_user_and_product(self, user_id, product_id):
    delete_id = """
      DELETE FROM ProductCategoryAssignmentTask
      WHERE user_id = ? AND product_id = ?
    """
    async with self.db.execute(delete_id, (user_id, product_id)) as cursor:
      return cursor.rowcount

  async def delete_by_user(self, user_id):
    delete_id = """
      DELETE FROM ProductCategoryAssignmentTask
      WHERE user_id = ?
    """
    async with self.db.execute(delete_id, (user_id,)) as cursor:
      return cursor.rowcount
    