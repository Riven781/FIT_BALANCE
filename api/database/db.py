import aiosqlite
from config import DB_PATH
from api.database.create_db import product_table_query, product_category_table_query, product_category_closure_query



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
    await db.execute(product_category_table_query)
    await db.execute(product_category_closure_query)

    await db.commit()

async def reset_db():
  async with aiosqlite.connect(DB_PATH) as db:
    await db.execute("PRAGMA foreign_keys = OFF")

    await db.execute("DROP TABLE IF EXISTS product_category_closure")
    await db.execute("DROP TABLE IF EXISTS product")
    await db.execute("DROP TABLE IF EXISTS product_category")

    await db.execute("PRAGMA foreign_keys = ON")


    await db.execute(product_table_query)
    await db.execute(product_category_table_query)
    await db.execute(product_category_closure_query)

    await db.commit()