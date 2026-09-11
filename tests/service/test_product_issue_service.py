import pytest
from product_catalog_context.application.product_issue_service import ProductIssueService
from product_catalog_context.domain.issues.product_issue_status import ProductIssueStatus
from product_catalog_context.domain.errors import IssueCanNotBeConfirmed, IssueCanNotBeMarkedAsObsolete, IssueCanNotBeRejected
from product_catalog_context.application.errors.errors import IssueNotFoundError

pytestmark = pytest.mark.usefixtures('insert_data')

@pytest.mark.asyncio
async def test_confirm_issue(product_issue_service: ProductIssueService):
  product_issue = await product_issue_service.confirm_issue(1, 30, moderator_id=1)
  assert product_issue.status == ProductIssueStatus.CONFIRMED

@pytest.mark.asyncio
async def test_confirm_rejected_issue(product_issue_service: ProductIssueService):
  with pytest.raises(IssueCanNotBeConfirmed):
    product_issue = await product_issue_service.confirm_issue(4, 30, moderator_id=1)

@pytest.mark.asyncio
async def test_confirm_confirmed_issue(product_issue_service: ProductIssueService):
  with pytest.raises(IssueCanNotBeConfirmed):
    product_issue = await product_issue_service.confirm_issue(2, 30, moderator_id=1)

@pytest.mark.asyncio
async def test_confirm_not_existing_issue(product_issue_service: ProductIssueService):
  with pytest.raises(IssueNotFoundError):
    product_issue = await product_issue_service.confirm_issue(10001, 30, moderator_id=1)

@pytest.mark.asyncio
async def test_reject_pending_issue(product_issue_service: ProductIssueService):
  product_issue = await product_issue_service.reject_issue(1, moderator_id=1)
  assert product_issue.status == ProductIssueStatus.REJECTED

@pytest.mark.asyncio
async def test_reject_rejected_issue(product_issue_service: ProductIssueService):
  with pytest.raises(IssueCanNotBeRejected):
    product_issue = await product_issue_service.reject_issue(4, moderator_id=1)

@pytest.mark.asyncio
async def test_reject_confirmed_issue(product_issue_service: ProductIssueService):
  with pytest.raises(IssueCanNotBeRejected):
    product_issue = await product_issue_service.reject_issue(2, moderator_id=1)

@pytest.mark.asyncio
async def test_reject_not_existing_issue(product_issue_service: ProductIssueService):
  with pytest.raises(IssueNotFoundError):
    product_issue = await product_issue_service.reject_issue(10001, moderator_id=1)