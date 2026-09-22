from product_catalog_context.domain.issues.confirmation_saga.product_issue_confirmation_saga_repository import ProductIssueConfirmationSagaRepository
from product_catalog_context.infrastructure.sql_alchemy_repository.sqlalchemy_repository import BaseSqlAlchemyRepository
from product_catalog_context.domain.issues.confirmation_saga.product_issue_confirmation_saga import ProductIssueConfirmationSaga
import sqlalchemy.dialects.sqlite as sqlite
from product_catalog_context.infrastructure.sql_alchemy_repository.mapper import id_seq_table


class SqlAlchemyProductIssueConfirmationSagaRepository(ProductIssueConfirmationSagaRepository, BaseSqlAlchemyRepository):
  def __init__(self, session):
    super().__init__(session)

  async def get_by_id(self, saga_id) -> ProductIssueConfirmationSaga | None:
    return await self.session.get(ProductIssueConfirmationSaga, saga_id)
  
  async def save(self, saga: ProductIssueConfirmationSaga):
    await self._save(saga)

  async def next_id(self):
    query = (
      sqlite.insert(id_seq_table)
      .values(
        name = 'issue_confirmation_saga',
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