from product_catalog_context.domain.category_hierarchy.product_category_hierarchy import ProductCategoryHierarchy
from product_catalog_context.domain.category_hierarchy.product_category_hierarchy_repository import ProductCategoryHierarchyRepository
from product_catalog_context.infrastructure.sql_alchemy_repository.sqlalchemy_repository import BaseSqlAlchemyRepository
from sqlalchemy import delete, event, exists, func, insert, select
from product_catalog_context.domain.category_hierarchy.product_category_hierarchy_status import ProductCategoryHierarchyStatus
from product_catalog_context.infrastructure.sql_alchemy_repository.mapper import id_seq_table
import sqlalchemy.dialects.sqlite as sqlite

class SqlAlchemyProductCategoryHierarchyRepository(ProductCategoryHierarchyRepository, BaseSqlAlchemyRepository):
  def __init__(self, session):
    super().__init__(session)

  async def get_by_id(self, hierarchy_id):
    return await self.session.get(ProductCategoryHierarchy, hierarchy_id)

  async def get_draft(self) -> ProductCategoryHierarchy | None:
    query = select(ProductCategoryHierarchy).where(ProductCategoryHierarchy.status == ProductCategoryHierarchyStatus.DRAFT)
    result = await self._execute(query)
    return result.scalar_one_or_none()

  async def get_planned_for_publication(self) -> ProductCategoryHierarchy | None:
    query = select(ProductCategoryHierarchy).where(ProductCategoryHierarchy.status == ProductCategoryHierarchyStatus.PLANNED_FOR_PUBLICATION)
    result = await self._execute(query)
    return result.scalar_one_or_none()

  async def get_active(self) -> ProductCategoryHierarchy | None:
    query = select(ProductCategoryHierarchy).where(ProductCategoryHierarchy.status == ProductCategoryHierarchyStatus.ACTIVE)
    result = await self._execute(query)
    return result.scalar_one_or_none()

  async def save(self, hierarchy: ProductCategoryHierarchy):
    await self._save(hierarchy)

  async def delete(self, hierarchy: ProductCategoryHierarchy):
    await self.session.delete(hierarchy)

  async def delete_active(self):
    query = delete(ProductCategoryHierarchy).where(ProductCategoryHierarchy.status == ProductCategoryHierarchyStatus.ACTIVE)
    await self.session.execute(query)

  async def next_category_id(self):
    query = (
      sqlite.insert(id_seq_table)
      .values(
        name = 'product_category',
        next_value=100
      ).on_conflict_do_update(
        index_elements=[id_seq_table.c.name],
        set_= {
          "next_value" : id_seq_table.c.next_value + 1
        }
      )
      .returning(
        (id_seq_table.c.next_value - 1).label('id')
      )
    )
    result = await self._execute(query)
    return result.scalar_one()