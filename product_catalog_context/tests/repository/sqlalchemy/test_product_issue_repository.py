import pytest
from product_catalog_context.domain.issues.product_issue_repository import ProductIssueRepository
from product_catalog_context.domain.enums.reported_field import ReportedField
from product_catalog_context.domain.issues.product_issue_status import ProductIssueStatus
from product_catalog_context.domain.issues.product_issue import ProductIssue


pytestmark = pytest.mark.usefixtures("insert_data")

@pytest.mark.asyncio
async def test_get_by_id(product_issue_repository: ProductIssueRepository):
  issue = await product_issue_repository.get_by_id(1)
  assert issue.issue_id == 1
  assert issue.product_id == 1
  assert issue.reported_field == ReportedField.KCAL
  assert issue.status == ProductIssueStatus.PENDING
  assert issue.resolved_by is None



@pytest.mark.asyncio
async def test_get_by_id_not_existing_issue(product_issue_repository: ProductIssueRepository):
  issue = await product_issue_repository.get_by_id(100)
  assert issue is None

@pytest.mark.asyncio
async def test_get_pending_issue(product_issue_repository: ProductIssueRepository):
  issue = await product_issue_repository.get_pending_issue(product_id=1, reported_field=ReportedField.SUGARS)
  assert issue.issue_id == 3
  assert issue.product_id == 1
  assert issue.reported_field == ReportedField.SUGARS
  assert issue.status == ProductIssueStatus.PENDING

@pytest.mark.asyncio
async def test_get_pending_issue_by_not_existing_field(product_issue_repository: ProductIssueRepository):
  issue = await product_issue_repository.get_pending_issue(product_id=1, reported_field=ReportedField.CARBOHYDRATES)
  assert issue is None

@pytest.mark.asyncio
async def test_save_new_issue(product_issue_repository: ProductIssueRepository):
  new_issue = ProductIssue(product_id=5, reported_field=ReportedField.FAT, status=ProductIssueStatus.REJECTED)
  await product_issue_repository.save(new_issue)
  issue = await product_issue_repository.get_by_id(new_issue.issue_id)
  assert issue.issue_id == new_issue.issue_id
  assert issue.product_id == 5
  assert issue.reported_field == ReportedField.FAT
  assert issue.status == ProductIssueStatus.REJECTED


@pytest.mark.asyncio
async def test_save_updated_issue(product_issue_repository: ProductIssueRepository):
  issue = await product_issue_repository.get_by_id(1)
  issue.reject(user_id=10)
  await product_issue_repository.save(issue)
  updated_issue = await product_issue_repository.get_by_id(1)
  assert updated_issue.issue_id == 1
  assert updated_issue.product_id == 1
  assert updated_issue.reported_field == ReportedField.KCAL
  assert updated_issue.status == ProductIssueStatus.REJECTED
  assert updated_issue.resolved_by == 10


@pytest.mark.asyncio
async def test_delete_issue(product_issue_repository: ProductIssueRepository, db_session):
  issue = await product_issue_repository.get_by_id(1)
  await product_issue_repository.delete(issue)
  await db_session.commit()
  issue = await product_issue_repository.get_by_id(1)
  assert issue is None

