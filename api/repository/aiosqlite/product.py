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

  def _convert_category(self, result_dict):
    if result_dict['category_str'] is not None:
      category_ids_str, category_names_str = result_dict['category_str'].split(':')
      category_ids = category_ids_str.split('|')
      category_names = category_names_str.split('|')
      result_dict['category'] = [{"id":id, "name":name} for id, name in zip(category_ids, category_names)]
    else:
      result_dict['category'] = []


  async def get_total(self, category_id=None):
    total_query = f"""
      SELECT COUNT(*) AS total
      FROM Product AS prod
      {f"JOIN ProductCategoryClosure prodcc ON prod.category_id = prodcc.subcategory_id WHERE prodcc.supercategory_id = {category_id}"if category_id is not None else ''}
    """
    async with self.db.execute(total_query) as cursor:
      total_row = await cursor.fetchone()
      return total_row['total']

  async def get_all(self, page=1, limit=20, category_id=None):
    offset = (page - 1) * limit
    get_all_query = f"""
      SELECT prod.*, (
        SELECT GROUP_CONCAT(category_id, '|') || ':' || GROUP_CONCAT(category_name, '|') as category FROM (
          SELECT pc.id AS category_id, pc.name AS category_name 
            FROM ProductCategoryClosure AS pcc
            JOIN ProductCategory AS pc ON pc.id = pcc.supercategory_id
            WHERE pcc.subcategory_id = prod.category_id
            ORDER BY pcc.depth DESC
        )
      ) AS category_str 
      FROM Product as prod
      {f"JOIN ProductCategoryClosure prodcc ON prod.category_id = prodcc.subcategory_id WHERE prodcc.supercategory_id = {category_id}"if category_id is not None else ''}
      ORDER BY prod.id
      LIMIT ?
      OFFSET ?
    """
    async with self.db.execute(get_all_query, (limit, offset)) as cursor:
      result = await cursor.fetchall()
      if result is None:
        return None
      
      output_list = []

      for row in result:
        row_dict = dict(row)
        self._convert_category(row_dict)
        output_list.append(row_dict)

      

      return output_list

    
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
      self._convert_category(result_dict)
  
      return result_dict

      