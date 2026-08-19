import pytest
from product_catalog_context.infrastructure.aiosqlite_repository.product_issue_repository import ProductIssueRepository
from product_catalog_context.domain.issues.product_issue import ProductIssue
from product_catalog_context.domain.enums.product_issue_status import ProductIssueStatus


async def insert_issues(db):
  cursor = await db.executescript("""
    INSERT INTO Product (id, name, brand_name, kcal, reference_amount, reference_unit, name_search_standard)
      VALUES 
      (1, "Schab Drogi", "Auchan", 300, 100, "g","schab drogi"),
      (2, "Schab Tani", "Rambert", 250, 100, "g", "schab tani"),
      (3, "Schab Średni", "XYZ", 400, 100, "g", "schab sredni");
     
      
    INSERT INTO ProductIssue (id, product_id, reported_field, status, resolved_value)
      VALUES 
      (1, 1, 'kcal', 'pending', NULL),
      (2, 1, 'fat', 'rejected', NULL),
      (3, 1, 'sugar', 'confirmed', 21),
      (4, 2, 'kcal', 'pending', NULL);      
  """)
  await db.commit()
  await cursor.close()

@pytest.mark.asyncio
async def test_get_by_id(db):
  await insert_issues(db)
  repo = ProductIssueRepository(db)
  issue = await repo.get_by_id(1)
  assert issue.issue_id == 1
  assert issue.product_id == 1
  assert issue.reported_field == 'kcal'
  assert issue.status == ProductIssueStatus.PENDING

@pytest.mark.asyncio
async def test_get_by_not_existing__id(db):
  await insert_issues(db)
  repo = ProductIssueRepository(db)
  issue = await repo.get_by_id(100)
  assert issue is None

@pytest.mark.asyncio
async def test_get_pending_issue(db):
  await insert_issues(db)
  repo = ProductIssueRepository(db)
  issue = await repo.get_pending_issue(1, 'kcal')
  assert issue.issue_id == 1
  assert issue.product_id == 1
  assert issue.reported_field == 'kcal'
  assert issue.status == ProductIssueStatus.PENDING

@pytest.mark.asyncio
async def test_get_pending_not_existing_issue(db):
  await insert_issues(db)
  repo = ProductIssueRepository(db)
  issue = await repo.get_pending_issue(4, 'kcal')
  assert issue is None


@pytest.mark.asyncio
async def test_update_issue(db):
  await insert_issues(db)
  repo = ProductIssueRepository(db)
  issue = await repo.get_by_id(1)
  issue.status = ProductIssueStatus.REJECTED
  await repo.update(issue.issue_id, issue)
  updated_issue = await repo.get_by_id(1)
  assert updated_issue.issue_id == 1
  assert updated_issue.product_id == 1
  assert updated_issue.reported_field == 'kcal'
  assert updated_issue.status == ProductIssueStatus.REJECTED

@pytest.mark.asyncio
async def test_insert_issue(db):
  await insert_issues(db)
  repo = ProductIssueRepository(db)
  issue = ProductIssue(reported_field='kcal', status=ProductIssueStatus.PENDING, product_id=3)
  await repo.insert(issue)
  issue = await repo.get_by_id(5)
  assert issue.issue_id == 5
  assert issue.product_id == 3
  assert issue.reported_field == 'kcal'
  assert issue.status == ProductIssueStatus.PENDING

@pytest.mark.asyncio
async def test_delete_issue(db):
  await insert_issues(db)
  repo = ProductIssueRepository(db)
  count = await repo.delete(1)
  issue = await repo.get_by_id(1)
  assert issue is None
  assert count == 1

@pytest.mark.asyncio
async def test_delete_not_existing_issue(db):
  await insert_issues(db)
  repo = ProductIssueRepository(db)
  count = await repo.delete(100)
  assert count == 0