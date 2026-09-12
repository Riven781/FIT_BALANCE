from sqlalchemy import delete, event, exists, func, insert, select

from product_catalog_context.domain.category_hierarchy.product_category_hierarchy_status import ProductCategoryHierarchyStatus
from product_catalog_context.domain.product.product_repository import ProductRepository
from product_catalog_context.domain.product.product import Product
from sqlalchemy.ext.asyncio import  AsyncSession
from product_catalog_context.infrastructure.sql_alchemy_repository.sqlalchemy_repository import BaseSqlAlchemyRepository
from product_catalog_context.infrastructure.sql_alchemy_repository.mapper import product_category_assignment_table, product_category_node_table, product_category_hierarchy_table, product_table,product_category_assignment_task_table
class SqlAlchemyProductRepository(ProductRepository, BaseSqlAlchemyRepository):
  def __init__(self, session: AsyncSession):
    super().__init__(session)

  async def get_by_id(self, product_id) -> Product:
    @event.listens_for(Product, "load")
    def receive_load(product, context):
      product._events = []
    return await self.session.get(Product, product_id)

  async def delete(self, product: Product):
    await self.session.delete(product)

  async def save(self, product: Product):
    await self._save(product)

  async def get_total_without_planned_category(self):
    subquery = (
      select(1)
      .select_from(product_category_assignment_table)
      .join(product_category_node_table, product_category_node_table.c.id == product_category_assignment_table.c.node_id)
      .join(product_category_hierarchy_table, product_category_hierarchy_table.c.id == product_category_node_table.c.hierarchy_id)
      .where(product_category_assignment_table.c.product_id == product_table.c.id, product_category_hierarchy_table.c.status == ProductCategoryHierarchyStatus.PLANNED_FOR_PUBLICATION)
    )
    query = select(
      func.count().label("total_without_planned_category")
    ).select_from(
      product_table
    ).where(
      ~exists(subquery)
    )
    result = await self._execute(query)
    return result.scalar_one()

  async def get_without_planned_category_and_assignment_task(self, category_id, hierarchy_id, limit= 20) -> list[Product]:  #by active category
    subquery_1 = (
      select(1).select_from(product_category_assignment_table)
      .join(product_category_node_table, product_category_node_table.c.id == product_category_assignment_table.c.node_id)
      .join(product_category_hierarchy_table, product_category_hierarchy_table.c.id == product_category_node_table.c.hierarchy_id)
      .where(product_category_assignment_table.c.product_id == product_table.c.id, product_category_hierarchy_table.c.status == ProductCategoryHierarchyStatus.PLANNED_FOR_PUBLICATION)
    )
    subquery_2 = (
      select(1).select_from(product_category_assignment_task_table)
      .where(product_category_assignment_task_table.c.hierarchy_id == hierarchy_id, product_category_assignment_task_table.c.product_id == product_table.c.id)
    )
    query = select(Product).select_from(
      product_table
    ).join(
      product_category_assignment_table, product_category_assignment_table.c.product_id == product_table.c.id
    ).where(
      product_category_assignment_table.c.node_id == category_id, ~exists(subquery_1), ~exists(subquery_2)
    ).limit(limit)
    result = await self._execute(query)

    return list(result.scalars().all())

  async def copy_category_assignments(self, active_hierarchy_id, draft_hierarchy_id):
    active_node = product_category_node_table.alias("active_node")
    draft_node = product_category_node_table.alias("draft_node")

    select_query = (
      select(
        product_category_assignment_table.c.product_id,
        draft_node.c.id
      )
      .select_from(product_category_assignment_table)
      .join(active_node, active_node.c.id == product_category_assignment_table.c.node_id)
      .join(draft_node, active_node.c.id == draft_node.c.source_node_id)
      .where(
        active_node.c.hierarchy_id == active_hierarchy_id,
        draft_node.c.hierarchy_id == draft_hierarchy_id
      )
    )

    query = insert(product_category_assignment_table).from_select(
      ['product_id', 'node_id'],
      select_query
    )

    await self._execute(query)


  async def delete_category_assignments_by_category_id(self, category_ids):
    delete_query = delete(product_category_assignment_table).where(product_category_assignment_table.c.node_id.in_(category_ids))
    await self._execute(delete_query)
