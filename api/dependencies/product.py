from typing import Annotated

from fastapi import HTTPException, Path

from api.schemas.product import ProductDetailUpdate


def check_ids(product_id : Annotated[int, Path()], product: ProductDetailUpdate):
  if product.id is not None and product_id != product.id:
    raise HTTPException(status_code=400, detail='Bad request')