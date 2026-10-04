from typing import Annotated
from fastapi import APIRouter, Depends
from product_catalog_context.application.product_report_service import ProductReportService
from product_catalog_context.infrastructure.api.rest.dependencies.database import get_current_user_id, get_product_report_service
from product_catalog_context.infrastructure.api.rest.schemas.product_report import ProductReportRequest, ProductReportResponse


product_report_router = APIRouter()

@product_report_router.post('/product-reports', response_model=ProductReportResponse)
async def create_report(
  request : ProductReportRequest,
  product_report_service: Annotated[ProductReportService, Depends(get_product_report_service)],
  user_id : Annotated[int, Depends(get_current_user_id)]
):
  return await product_report_service.create_report(request.to_command(), user_id)