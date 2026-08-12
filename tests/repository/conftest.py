

import pytest
import aiosqlite
import pytest_asyncio

from shared.database.create_new_db import product_table_query, product_category_node_table_query, product_category_hierarchy_query, product_category_assignment, product_category_closure_query, product_category_assignment_task
from shared.database.create_new_db import fields, report, report_item, issue, user, role, user_role

@pytest_asyncio.fixture
async def db():
  db = await aiosqlite.connect(":memory:") #tworzy nową dla każdego połączenia
  db.row_factory = aiosqlite.Row
  await db.execute("PRAGMA foreign_keys = ON")
  await db.execute(product_table_query)
  await db.execute(product_category_node_table_query)
  await db.execute(product_category_hierarchy_query)
  await db.execute(product_category_assignment)
  await db.execute(product_category_closure_query)
  await db.execute(product_category_assignment_task)
  await db.execute(fields)
  await db.execute(report)
  await db.execute(report_item)
  await db.execute(issue)
  await db.execute(user)
  await db.execute(role)
  await db.execute(user_role)


  await db.commit()

  yield db

  await db.close()

