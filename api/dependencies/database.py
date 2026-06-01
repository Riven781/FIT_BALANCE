from typing import Annotated

import aiosqlite
from fastapi import Depends

from api.database.db import get_db
from api.repository.aiosqlite.product import ProductRepository
from api.services.product import ProductService


async def get_product_repository(db: Annotated[aiosqlite.Connection, Depends(get_db)]):
  return ProductRepository(db)

async def get_product_service(product_repository: Annotated[ProductRepository, Depends(get_product_repository)]):
  return ProductService(product_repository)