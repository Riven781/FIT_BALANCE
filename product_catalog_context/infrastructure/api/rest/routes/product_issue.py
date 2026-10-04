from typing import Annotated
from fastapi import APIRouter, Depends
from product_catalog_context.application.product_issue_service import ProductIssueService
from product_catalog_context.infrastructure.api.rest.dependencies.database import get_current_user_id, get_product_issue
from product_catalog_context.infrastructure.api.rest.schemas.product_issue import ConfirmIssueRequest, ProductIssueResponse

product_issue_router = APIRouter()

@product_issue_router.put('/product-issues/{issue_id}/confirm', response_model=ProductIssueResponse, status_code=202)
async def confirm_issue(
  issue_id: int,
  request: ConfirmIssueRequest,
  product_issue_service: Annotated[ProductIssueService, Depends(get_product_issue)],
  user_id : Annotated[int, Depends(get_current_user_id)]
):
  return await product_issue_service.confirm_issue(issue_id, request.resolved_value, user_id)

@product_issue_router.put('/product-issues/{issue_id}/reject',  response_model=ProductIssueResponse)
async def reject_issue(
  issue_id: int,
  product_issue_service: Annotated[ProductIssueService, Depends(get_product_issue)],
  user_id : Annotated[int, Depends(get_current_user_id)]
):
  return await product_issue_service.reject_issue(issue_id, user_id)