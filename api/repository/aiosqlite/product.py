
import aiosqlite
from api.dependencies.filters import ProductsFilters
from api.enums.product import NameMode, SortBy, ViewMode
from api.repository.aiosqlite.repository import DbRepository
from api.schemas.product import ProductCreate, ProductDetail, ProductSummary, ProductUpdate


class ProductRepository(DbRepository):
  def __init__(self, db : aiosqlite.Connection):
    super().__init__(db, 'Product')

  def _convert_category(self, result_dict):
    if result_dict['category_str'] is not None:
      category_ids_str, category_names_str = result_dict['category_str'].split(':')
      category_ids = category_ids_str.split('|')
      category_names = category_names_str.split('|')
      result_dict['category'] = [{"id":id, "name":name} for id, name in zip(category_ids, category_names)]
    else:
      result_dict['category'] = []

  def _translate_filters_to_query(self, category_id = None, names = None):
    conditions = []
    inner_query = ''
    arguments = []
    if category_id is not None:
      inner_query +=' JOIN ProductCategoryClosure prodcc ON prod.category_id = prodcc.subcategory_id '
      conditions.append('prodcc.supercategory_id = ?') 
      arguments.append(category_id)
    if names is not None:
      name_query = f"({' AND '.join(['(prod.name_search_standard LIKE ? OR prod.name_search_standard LIKE ?)' for _ in range(len(names))])})"
      conditions.append(name_query)

      for name in names:
        arguments.append(f'% {name}%')
        arguments.append(f'{name}%')

    where_query = None
    if conditions:
      where_query = 'WHERE ' + " AND ".join(conditions)
    return inner_query, where_query, arguments


  async def get_total(self, category_id = None, names = None):
    inner_query, where_query, arguments = self._translate_filters_to_query(category_id=category_id, names=names)

    total_query = f"""
      SELECT COUNT(*) AS total
      FROM Product AS prod
      {inner_query}
      {where_query if where_query is not None else " "}
    """
    async with self.db.execute(total_query, arguments) as cursor:
      total_row = await cursor.fetchone()
      return total_row['total']
    

  async def get_by_filters(self, category_id=None, names=None, sort_by=SortBy.KCAL, order="ASC", page=1, limit=20):
    offset = (page - 1) * limit
    inner_query, where_query, arguments = self._translate_filters_to_query(category_id, names)

    get_by_filters_query = f"""
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
      ORDER BY {sort_by.value} {order}
      LIMIT ?
      OFFSET ?
    """
    async with self.db.execute(get_by_filters_query, (*arguments, limit, offset)) as cursor:
      result = await cursor.fetchall()
      if result is None:
        return None
      
      output_list = []

      for row in result:
        row_dict = dict(row)
        self._convert_category(row_dict)
        
        output_list.append(ProductDetail(**row_dict))
        
      return output_list

    
  async def get_by_id(self, id):
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

  
    return ProductDetail(**result_dict)

      