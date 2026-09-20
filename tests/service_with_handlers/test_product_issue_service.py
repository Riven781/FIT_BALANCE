import pytest
import pytest_asyncio
import asyncio
from product_catalog_context.application.product_issue_service import ProductIssueService
from product_catalog_context.domain.product.product_repository import ProductRepository
from product_catalog_context.infrastructure.outbox.repository import OutboxDAO


pytestmark = pytest.mark.usefixtures('insert_data', 'outbox_dispatcher')

@pytest.mark.asyncio
async def test_confirm_issue(product_issue_service: ProductIssueService, product_repository: ProductRepository, outbox_dao: OutboxDAO, db_session):
  await product_issue_service.confirm_issue(issue_id=1, resolved_value=120, moderator_id=100)
  outbox_message = await outbox_dao.get_by_id(1)
  assert outbox_message is not None
  await asyncio.sleep(1)
  product = await product_repository.get_by_id(1)
 
  assert product.kcal == 120


@pytest.mark.asyncio
async def test_confirm_2_issues(product_issue_service: ProductIssueService, product_repository: ProductRepository, outbox_dao: OutboxDAO, db_session):
  await product_issue_service.confirm_issue(issue_id=1, resolved_value=120, moderator_id=100)
  await product_issue_service.confirm_issue(issue_id=3, resolved_value=10, moderator_id=100)
  await db_session.commit()
  
  await asyncio.sleep(10)
  product = await product_repository.get_by_id(1)
  
  assert product.kcal == 120
  assert product.sugars == 10