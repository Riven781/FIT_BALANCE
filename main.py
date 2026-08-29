from contextlib import asynccontextmanager
from enum import Enum
from os import name
import re
from unittest import result
import aiofiles
import asyncio
from fastapi.encoders import jsonable_encoder
from identity_and_access_context.infrastructure.api.rest.error_handlers import register_identity_and_access_exception_handlers
from shared.database.db import init_db, reset_db
from product_catalog_context.infrastructure.api.rest.error_handlers import invalid_product_category_id_handler, invalid_product_data_handler, product_already_exists_handler, product_not_found_handler, register_exception_handlers, repository_error_handler
from product_catalog_context.infrastructure.aiosqlite_repository.product import ProductRepository
from product_catalog_context.infrastructure.aiosqlite_repository.errors.errors import RepositoryError
from product_catalog_context.infrastructure.api.rest.schemas.product_category import ProductCategory, ProductCategoryHierarchy
from product_catalog_context.application.errors.errors import InvalidProductCategoryId, InvalidProductDataError, ProductAlreadyExistsError, ProductNotFoundError
from pydantic import BaseModel, Field
from fastapi import Body, Depends, FastAPI, HTTPException, Path, Query
from typing import Annotated, Literal
import json
import math

from product_catalog_context.application.category_hierarchy_management_service import ProductCategoryService
from config import MODE
import aiosqlite
from product_catalog_context.infrastructure.api.rest.routes import product_catalog_router
#python api\endpoints.py

@asynccontextmanager
async def lifespan(app: FastAPI):
  if MODE == 'TEST':
    await reset_db()
  else:
    await init_db()
  yield

app = FastAPI(lifespan=lifespan)
register_exception_handlers(app)
register_identity_and_access_exception_handlers(app)
app.include_router(product_catalog_router)
