import aiosqlite
from product_catalog_context.infrastructure.aiosqlite_queries.mapper import to_product_detail
from product_catalog_context.infrastructure.aiosqlite_repository.errors_mapper import map_errors
from product_catalog_context.domain.enums.product_searching import NameMode, SortBy


class ProductQueries:
  def __init__(self, db : aiosqlite.Connection):
    self.db = db

  def _translate_filters_to_query(self, category_id = None, names = None):
    conditions = []
    inner_query = ''
    arguments = []
    if category_id is not None:
      inner_query += """
        JOIN ProductCategoryAssignment assignment ON assignment.product_id = prod.id
        JOIN ProductCategoryClosure prodcc ON assignment.node_id = prodcc.subcategory_id
      """
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
    try:
      async with self.db.execute(total_query, arguments) as cursor:
        total_row = await cursor.fetchone()
    except Exception as e:
      raise map_errors(e) from e
      
    return total_row['total']

  def _convert_category(self, result_dict):
    if result_dict['category_str'] is not None:
      category_ids_str, category_names_str = result_dict['category_str'].split(':')
      category_ids = category_ids_str.split('|')
      category_names = category_names_str.split('|')
      result_dict['category'] = [{"id":id, "name":name} for id, name in zip(category_ids, category_names)]
    else:
      result_dict['category'] = []

  async def get_detail_by_filters(self, category_id=None, names=None, sort_by=SortBy.KCAL, order="ASC", page=1, limit=20):
    offset = (page - 1) * limit
    inner_query, where_query, arguments = self._translate_filters_to_query(category_id, names)

    get_by_filters_query = f"""
    SELECT prod.*, (
        SELECT GROUP_CONCAT(category_id, '|') || ':' || GROUP_CONCAT(category_name, '|') as category FROM (
          SELECT node.id AS category_id, node.name AS category_name 
            FROM ProductCategoryClosure AS pcc
            JOIN ProductCategoryAssignment assignment ON assignment.node_id = pcc.subcategory_id
            JOIN ProductCategoryNode AS node ON node.id = pcc.supercategory_id
            WHERE assignment.product_id = prod.id
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
    try:
      async with self.db.execute(get_by_filters_query, (*arguments, limit, offset)) as cursor:
        result = await cursor.fetchall()
    except Exception as e:
      print(e)
      raise map_errors(e) from e
    
    if result is None:
      return None  
    output_list = []

    for row in result:
      row_dict = dict(row)
      #self._convert_category(row_dict)
      product = to_product_detail(row_dict)
      output_list.append(product)
    return output_list

  
  async def get_detail_by_id(self, id):
    get_query = """
      SELECT prod.*, (
        SELECT  GROUP_CONCAT(category_id, '|') || ':' || GROUP_CONCAT(category_name, '|') as category FROM 
          (SELECT node.id AS category_id, node.name AS category_name FROM ProductCategoryClosure as pcc
            JOIN ProductCategoryAssignment assignment ON assignment.node_id = pcc.subcategory_id
            JOIN ProductCategoryNode AS node ON node.id = pcc.supercategory_id
            WHERE assignment.product_id = prod.id
            ORDER BY pcc.depth DESC)
      ) AS category_str FROM Product as prod WHERE id = ?
    """
    try:
      async with self.db.execute(get_query, (id,)) as cursor:
        result = await cursor.fetchone()
    except Exception as e:
      raise map_errors(e) from e
    
    if result is None:
      return None
    result_dict = dict(result)
    #self._convert_category(result_dict)

    product_detail = to_product_detail(result_dict)

    return product_detail