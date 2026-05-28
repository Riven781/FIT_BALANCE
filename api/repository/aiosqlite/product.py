from typing import Annotated

import aiosqlite
from fastapi import Depends

from api.dependencies.filters import ProductsFilters
from api.enums.product import NameMode, ViewMode
from api.schemas.product import ProductDetail, ProductSummary



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

  def _translate_filters_to_query(self, products_filters : ProductsFilters):
    conditions = []
    inner_query = ''
    arguments = []
    if products_filters.category_id is not None:
      inner_query += ' JOIN ProductCategoryClosure prodcc ON prod.category_id = prodcc.subcategory_id '
      conditions.append('prodcc.supercategory_id = ?') 
      arguments.append(products_filters.category_id)
    if products_filters.name is not None:
      if products_filters.name_mode == NameMode.EXAC:
        conditions.append('LOWER(prod.name) = LOWER(?)')
        arguments.append(products_filters.name)
      elif products_filters.name_mode == NameMode.CONTAINS:
        conditions.append('LOWER(prod.name) LIKE LOWER(?)')
        arguments.append(f'%{products_filters.name}%')

    where_query = None
    if conditions:
      where_query = 'WHERE ' + " AND ".join(conditions)
    return inner_query, where_query, arguments


  async def get_total(self, products_filters):
    inner_query, where_query, arguments = self._translate_filters_to_query(products_filters)

    total_query = f"""
      SELECT COUNT(*) AS total
      FROM Product AS prod
      {inner_query}
      {where_query if where_query is not None else " "}
    """
    async with self.db.execute(total_query, arguments) as cursor:
      total_row = await cursor.fetchone()
      return total_row['total']

  async def get_all(self, products_filters ,page=1, limit=20):
    offset = (page - 1) * limit
    inner_query, where_query, arguments = self._translate_filters_to_query(products_filters)

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
      {inner_query}
      {where_query if where_query is not None else " "}
      ORDER BY {products_filters.sort_by.value} {products_filters.order}
      LIMIT ?
      OFFSET ?
    """
    async with self.db.execute(get_all_query, (*arguments, limit, offset)) as cursor:
      result = await cursor.fetchall()
      if result is None:
        return None
      
      output_list = []


      for row in result:
        row_dict = dict(row)
        self._convert_category(row_dict)
        
        output_list.append(ProductDetail(**row_dict) if products_filters.view_mode == ViewMode.DETAIL else ProductSummary(**row_dict))
        
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

      