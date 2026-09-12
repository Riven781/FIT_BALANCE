import aiosqlite
from product_catalog_context.infrastructure.aiosqlite_queries.mapper import to_product_detail
from product_catalog_context.infrastructure.aiosqlite_repository.errors_mapper import map_errors
from product_catalog_context.domain.enums.product_searching import NameMode, SortBy


from product_catalog_context.application.query.category_path_item import CategoryPathItem
from product_catalog_context.application.query.product_detail import PublicProductDetail
from product_catalog_context.domain.product.nutrition_facts import Nutrients, NutritionFacts, ReferenceQuantity


#def to_category_path_item():
#  pass




class ProductQueries:
  def __init__(self, db : aiosqlite.Connection):
    self.db = db



  def _translate_filters_to_query(self, category_id = None, names = None):
    conditions = []
    inner_query = ''
    arguments = []
    if category_id is not None:
      inner_query += """
        JOIN ProductCategoryAssignment as assignment_2 ON assignment_2.product_id = product.id
        JOIN ProductCategoryClosure AS closure_2  ON assignment_2.node_id = closure_2.subcategory_id AND closure_2.supercategory_id = ?
      """
      #conditions.append('closure_2.supercategory_id = ?') 
      arguments.append(category_id)
    if names is not None:
      name_query = f"({' AND '.join(['(product.name_search_standard LIKE ? OR product.name_search_standard LIKE ?)' for _ in range(len(names))])})"
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



  async def get_detail_by_filters(self, category_id=None, names=None, sort_by=SortBy.KCAL, order="ASC", page=1, limit=20):
    offset = (page - 1) * limit
    inner_query, where_query, arguments = self._translate_filters_to_query(category_id, names)

    get_by_filters_query = f"""
      SELECT product.*, node.id as category_id, node.name as category_name FROM (
        SELECT product.* FROM Product as product
        {inner_query}
        {where_query if where_query is not None else " "}
        ORDER BY product.{sort_by.value} {order}, product.id ASC
        LIMIT ?
        OFFSET ?
      ) as product
      LEFT JOIN ProductCategoryAssignment as assignment ON assignment.product_id = product.id
      LEFT JOIN ProductCategoryClosure as closure ON closure.subcategory_id = assignment.node_id
      LEFT JOIN ProductCategoryNode as node ON closure.supercategory_id = node.id
      ORDER BY product.{sort_by.value} {order}, product.id ASC, closure.depth DESC;

    """
    try:
      async with self.db.execute(get_by_filters_query, (*arguments, limit, offset)) as cursor:
        results = await cursor.fetchall()
    except Exception as e:
      print(e)
      raise map_errors(e) from e
    
    if results is None:
      return None  
    output_by_id = {}

    for row in results:
      if row['id'] not in output_by_id:
        if row['category_id'] is not None:
          categories = [CategoryPathItem(row['category_id'], row['category_name'])]
        else:
          categories = []
        output_by_id[row['id']] = to_product_detail(row, categories) 
      else:
        if row['category_id'] is not None:
          output_by_id[row['id']].category_path.append(CategoryPathItem(row['category_id'], row['category_name']))

      
    return list(output_by_id.values())
  


  async def get_detail_by_id(self, id):
    get_query = """
      SELECT product.*, node.id as category_id, node.name as category_name FROM Product as product
      LEFT JOIN ProductCategoryAssignment as assignment ON assignment.product_id = product.id
      LEFT JOIN ProductCategoryClosure as closure ON closure.subcategory_id = assignment.node_id
      LEFT JOIN ProductCategoryNode as node ON closure.supercategory_id = node.id
      WHERE product.id = ?
      ORDER BY product.id, closure.depth DESC;
    """
    try:
      async with self.db.execute(get_query, (id,)) as cursor:
        results = await cursor.fetchall()
    except Exception as e:
      raise map_errors(e) from e
    
    if not results:
      return None
    
    categories = [CategoryPathItem(row['category_id'], row['category_name']) for row in results if row['category_id']is not None]

    return to_product_detail(results[0], categories) 
