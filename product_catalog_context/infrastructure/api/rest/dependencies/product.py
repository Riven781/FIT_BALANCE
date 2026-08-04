from typing import Annotated

from fastapi import HTTPException, Path

from product_catalog_context.infrastructure.api.rest.schemas.product import ProductUpdate


def check_ids(product_id : Annotated[int, Path()], product: ProductUpdate):
  if product.id is not None and product_id != product.id:
    raise HTTPException(status_code=400, detail='Bad request')