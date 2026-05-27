from typing import Annotated

import aiosqlite
from fastapi import Depends



DB_PATH = './api/database/fit-balance.db'

async def get_db():
  db = await aiosqlite.connect(DB_PATH)
  db.row_factory = aiosqlite.Row
  await db.execute("PRAGMA foreign_keys = ON")
  try:
    yield db
  finally:
    await db.close()

class ProductRepository():
  def __init__(self, db : Annotated[aiosqlite.Connection, Depends(get_db)]):
    self.db = db

  async def get_all(self, page=1, limit=20):
    offset = (page - 1) * limit
    get_all_query = """
      SELECT * FROM Product
      LIMIT = ?
      OFFSET = ?
    """
    async with self.db.execute(get_all_query, (limit, offset)) as cursor:
      return await cursor.fetchall()
    
  async def get(self, id):
    get_query = """
      SELECT prod.*, (
        SELECT  GROUP_CONCAT(category_id, '|') || ':' || GROUP_CONCAT(category_name, '|') as category FROM 
          (SELECT pc.id AS category_id, pc.name AS category_name FROM ProductCategoryClosure as pcc
            JOIN ProductCategory as pc ON pc.id = pcc.supercategory_id
            WHERE pcc.subcategory_id = prod.category_id
            ORDER BY pcc.depth DESC)
      ) AS category_str FROM Product as prod WHERE id = ?
    """
    async with self.db.execute(get_query, (id,)) as cursor:
      result = await cursor.fetchone()
      if result is None:
        return None
      result_dict = dict(result)
  
      if result_dict['category_str'] is not None:
        category_ids_str, category_names_str = result_dict['category_str'].split(':')
        category_ids = category_ids_str.split('|')
        category_names = category_names_str.split('|')
        result_dict['category'] = [{"id":id, "name":name} for id, name in zip(category_ids, category_names)]
      else:
        result_dict['category'] = []
    
      return result_dict

      