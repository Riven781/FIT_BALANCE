import aiosqlite
from config import DB_PATH

from shared.database.create_new_db import product_table_query, product_category_node_table_query, product_category_hierarchy_query, product_category_assignment, product_category_closure_query, product_category_assignment_task
from shared.database.create_new_db import fields, report, report_item, issue, user, role, user_role, id_sequence, init_id_seq, user_roles, refresh_token


async def get_db():
  db = await aiosqlite.connect(DB_PATH)
  db.row_factory = aiosqlite.Row
  await db.execute("PRAGMA foreign_keys = ON")
  try:
    yield db
  finally:
    await db.close()


async def init_db():
  async with aiosqlite.connect(DB_PATH) as db:
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

async def reset_db():
  async with aiosqlite.connect(DB_PATH) as db:
    await db.execute("PRAGMA foreign_keys = OFF")

    await db.execute("DROP TABLE IF EXISTS Product")
    await db.execute("DROP TABLE IF EXISTS ProductCategoryNode")
    await db.execute("DROP TABLE IF EXISTS ProductCategoryHierarchy")
    await db.execute("DROP TABLE IF EXISTS ProductCategoryAssignment")
    await db.execute("DROP TABLE IF EXISTS ProductCategoryAssignmentTask")
    await db.execute("DROP TABLE IF EXISTS ProductCategoryClosure")
    await db.execute("DROP TABLE IF EXISTS Field")
    await db.execute("DROP TABLE IF EXISTS ProductReport")
    await db.execute("DROP TABLE IF EXISTS ProductReportItem")
    await db.execute("DROP TABLE IF EXISTS ProductIssue")
    await db.execute("DROP TABLE IF EXISTS User")
    await db.execute("DROP TABLE IF EXISTS Role")
    await db.execute("DROP TABLE IF EXISTS UserRole")
    await db.execute("DROP TABLE IF EXISTS IdSequence")

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
    await db.execute(user_roles)
    await db.execute(id_sequence)
    await db.execute(init_id_seq)
    await db.execute(refresh_token)


    await db.commit()
  async with aiosqlite.connect(DB_PATH) as db:
    await db.executescript("""
      INSERT INTO ProductCategoryHierarchy (id, status)
      VALUES (101, 'ACTIVE');
    """)
    await db.commit()
