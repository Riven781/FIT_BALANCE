from product_catalog_context.infrastructure.aiosqlite_repository.mapper import ProductIssueMapper
from product_catalog_context.infrastructure.aiosqlite_repository.repository import DbRepository


class ProductIssueRepository(DbRepository):
  def __init__(self, db, name='ProductIssue', mapper=ProductIssueMapper):
    super().__init__(db, name, mapper)

  async def get_by_id(self, id):
    get_query = """
    SELECT * FROM ProductIssue
    WHERE  id = ?
    """
    async with self.db.execute(get_query, (id,)) as cursor:
      row = await cursor.fetchone()
    if row is None:
      return None
    return self.mapper.to_issue(row)

  async def get_pending_issue(self, product_id, reported_field):
    get_query ="""
    SELECT * FROM ProductIssue
    WHERE product_id = ? AND reported_field = ? AND status='pending'
    """
    async with self.db.execute(get_query, (product_id, reported_field)) as cursor:
      row = await cursor.fetchone()
    if row is None:
      return None
    return self.mapper.to_issue(row)