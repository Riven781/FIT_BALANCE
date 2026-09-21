from sqlalchemy import delete, exists, insert, literal, select, func
from sqlalchemy.orm.exc import StaleDataError
from product_catalog_context.domain.tasks.category_assignment_task import CategoryAssignmentTask
from product_catalog_context.domain.tasks.category_assignment_task_repository import CategoryAssignmentTaskRepository
from product_catalog_context.infrastructure.sql_alchemy_repository.sqlalchemy_repository import BaseSqlAlchemyRepository
from product_catalog_context.infrastructure.sql_alchemy_repository.mapper import product_category_assignment_table, product_category_node_table, product_category_hierarchy_table, product_table,product_category_assignment_task_table


class SqlAlchemyCategoryAssignmentTaskRepository(CategoryAssignmentTaskRepository, BaseSqlAlchemyRepository):
  def __init__(self, session):
    super().__init__(session)

  async def get_by_id(self, task_id) -> CategoryAssignmentTask:
    return await self.session.get(CategoryAssignmentTask, task_id)

  async def get_by_product_and_hierarchy(self, product_id, hierarchy_id) -> CategoryAssignmentTask:
    query = select(CategoryAssignmentTask).where(CategoryAssignmentTask.product_id == product_id, CategoryAssignmentTask.hierarchy_id == hierarchy_id)
    result = await self._execute(query)
    return result.scalar_one_or_none()

  async def get_total_in_hierarchy(self, hierarchy_id) -> int:
    stmt = select(
      func.count(product_category_assignment_task_table.c.product_id.distinct())
    ).where(
      product_category_assignment_task_table.c.hierarchy_id == hierarchy_id
    )
    result = await self._execute(stmt)
    return result.scalar()

  async def insert_tasks_for_unassigned_products(self, user_id, hierarchy_id, limit):
    task_exists = select(1).select_from(product_category_assignment_task_table).where(
      product_category_assignment_task_table.c.product_id == product_table.c.id,
      product_category_assignment_task_table.c.hierarchy_id == hierarchy_id
    )
    assignment_exists = (
      select(1)
      .select_from(product_category_assignment_table)
      .join(product_category_node_table, product_category_node_table.c.id == product_category_assignment_table.c.node_id)
      .where(
        product_category_assignment_table.c.product_id == product_table.c.id,
        product_category_node_table.c.hierarchy_id == hierarchy_id
      )
    )
    products = select(
      product_table.c.id,
      literal(hierarchy_id),
      literal(user_id),
      literal('PENDING')
    ).where(
      ~exists(task_exists),
      ~exists(assignment_exists)
    ).order_by(
      product_table.c.id
    ).limit(limit)

    query = insert(product_category_assignment_task_table).from_select(
      ['product_id', 'hierarchy_id', 'user_id', 'status'],
      products
    )
    result = await self._execute(query)
    return result.rowcount

  async def delete_by_user(self, user_id):
    query = delete(CategoryAssignmentTask).where(CategoryAssignmentTask.user_id == user_id)
    result = await self._execute(query)
    return result.rowcount

  async def delete_by_user_and_product(self, user_id, product_id):
    query = delete(CategoryAssignmentTask).where(CategoryAssignmentTask.user_id == user_id, CategoryAssignmentTask.product_id == product_id)
    result = await self._execute(query)
    return result.rowcount

  async def delete_by_hierarchy(self, hierarchy_id):
    query = delete(CategoryAssignmentTask).where(CategoryAssignmentTask.hierarchy_id == hierarchy_id)
    await self._execute(query)

  async def delete(self, task: CategoryAssignmentTask):
    await self.session.delete(task)

  async def save(self, task: CategoryAssignmentTask):
    await self._save(task)



  async def insert_all(self, tasks: list[CategoryAssignmentTask]):
    data = [{k : v for k, v in task.__dict__.items() if not k.startswith('_')} for task in tasks]
    result = await self._execute(insert(CategoryAssignmentTask), data)
