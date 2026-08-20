import pytest
from product_catalog_context.application.product_issue_service import ProductIssueService
from product_catalog_context.domain.enums.product_issue_status import ProductIssueStatus
from product_catalog_context.domain.errors import IssueCanNotBeConfirmed, IssueCanNotBeMarkedAsObsolete, IssueCanNotBeRejected
from product_catalog_context.application.errors.errors import IssueNotFoundError


@pytest.mark.asyncio
async def test_confirm_issue(product_issue_service: ProductIssueService):
  product_issue = await product_issue_service.confirm_issue(100, 30)
  assert product_issue.status == ProductIssueStatus.CONFIRMED

@pytest.mark.asyncio
async def test_confirm_rejected_issue(product_issue_service: ProductIssueService):
  with pytest.raises(IssueCanNotBeConfirmed):
    product_issue = await product_issue_service.confirm_issue(99, 30)

@pytest.mark.asyncio
async def test_confirm_confirmed_issue(product_issue_service: ProductIssueService):
  with pytest.raises(IssueCanNotBeConfirmed):
    product_issue = await product_issue_service.confirm_issue(102, 30)

@pytest.mark.asyncio
async def test_confirm_not_existing_issue(product_issue_service: ProductIssueService):
  with pytest.raises(IssueNotFoundError):
    product_issue = await product_issue_service.confirm_issue(10001, 30)

@pytest.mark.asyncio
async def test_reject_pending_issue(product_issue_service: ProductIssueService):
  product_issue = await product_issue_service.reject_issue(100)
  assert product_issue.status == ProductIssueStatus.REJECTED

@pytest.mark.asyncio
async def test_reject_rejected_issue(product_issue_service: ProductIssueService):
  with pytest.raises(IssueCanNotBeRejected):
    product_issue = await product_issue_service.reject_issue(99)

@pytest.mark.asyncio
async def test_reject_confirmed_issue(product_issue_service: ProductIssueService):
  with pytest.raises(IssueCanNotBeRejected):
    product_issue = await product_issue_service.reject_issue(102)

@pytest.mark.asyncio
async def test_reject_not_existing_issue(product_issue_service: ProductIssueService):
  with pytest.raises(IssueNotFoundError):
    product_issue = await product_issue_service.reject_issue(10001)