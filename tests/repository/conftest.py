import pytest
import aiosqlite
import pytest_asyncio

from api.database.create_db import product_table_query, product_category_table_query, product_category_closure_query

@pytest_asyncio.fixture
async def db():
  db = await aiosqlite.connect(":memory:") #tworzy nową dla każdego połączenia
  db.row_factory = aiosqlite.Row
  await db.execute("PRAGMA foreign_keys = ON")
  await db.execute(product_table_query)
  await db.execute(product_category_table_query)
  await db.execute(product_category_closure_query)

  await db.commit()

  yield db

  await db.close()
