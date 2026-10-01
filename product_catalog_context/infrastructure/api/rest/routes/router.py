from fastapi import APIRouter
from product_catalog_context.infrastructure.api.rest.routes.product import product_router
product_catalog_router = APIRouter()

product_catalog_router.include_router(product_router)