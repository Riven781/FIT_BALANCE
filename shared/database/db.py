import asyncio
from pathlib import Path

import aiosqlite
from config import DB_PATH

from identity_and_access_context.infrastructure.security import hash_value
from shared.database.create_new_db import product_table_query, product_category_node_table_query, product_category_hierarchy_query, product_category_assignment, product_category_closure_query, product_category_assignment_task
from shared.database.create_new_db import fields, report, report_item, issue, user, role, user_role, id_sequence, init_id_seq, user_roles, refresh_token
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from product_catalog_context.infrastructure.sql_alchemy_repository.mapper import mapper_registry
from product_catalog_context.infrastructure.outbox.mapper import outbox_mapper_registry
from sqlalchemy import event
from identity_and_access_context.infrastructure.sql_alchemy_repository.mapper import mapper_registry as ia_registry
async def get_db():
  print("QUERY DB:", Path(DB_PATH).resolve())

  db = await aiosqlite.connect(DB_PATH)
  db.row_factory = aiosqlite.Row
  await db.execute("PRAGMA foreign_keys = ON")
  async with db.execute("PRAGMA table_info(Product)") as cursor:
    rows = await cursor.fetchall()
    print("PRODUCT COLUMNS:", [row["name"] for row in rows])
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


async def insert_data():
  async with aiosqlite.connect(DB_PATH) as db:
    password = 'strong_password'
    hashed_password = hash_value(password)

    password = "strong_password"
    hashed_password = hash_value(password)

    await db.executemany(
        """
        INSERT INTO User(id, username, email, hashed_password)
        VALUES (?, ?, ?, ?)
        """,
        [
            (1000, "Pawlo", "pawlo@gm.c", hashed_password),
            (2000, "Adam", "adam@gm.c", hashed_password),
            (3000, "Agata", "agata@gm.c", hashed_password),
        ],
    )

    await db.executescript("""
      INSERT INTO UserRoles(user_id, version) VALUES 
        (1000, 1), 
        (2000, 1),
        (3000, 1);
      
      INSERT INTO UserRole(user_id, role) VALUES 
        (1000, 'product_editor'),
        (1000, 'catalog_manager'),
        (1000, 'moderator'),
        (2000, 'product_editor'),
        (3000, 'product_editor');

    INSERT INTO ProductCategoryHierarchy (id, status, version)
      VALUES (101, 'ACTIVE', 0);

    INSERT INTO ProductCategoryNode (id, name, parent_id, hierarchy_id) VALUES
    (200, 'Produkty', NULL, 101),
    (201, 'Zwierzęce', 200, 101),
    (202, 'Roślinne', 200, 101),
    (203, 'Mleko', 201, 101),
    (204, 'Ciasto', 202, 101);

    INSERT INTO ProductCategoryClosure (supercategory_id, subcategory_id, depth) VALUES
    (200, 200, 0),
    (200, 201, 1),
    (200, 202, 1),
    (200, 203, 2),
    (200, 204, 2),
    (201, 201, 0),
    (201, 203, 1),
    (202, 202, 0),
    (202, 204, 1),
    (203, 203, 0),
    (204, 204, 0);
    """)
    await db.commit()



async def reset_db():
  engine = create_async_engine(f'sqlite+aiosqlite:///{DB_PATH}')
  session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

  @event.listens_for(engine.sync_engine, 'connect')
  def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute('PRAGMA foreign_keys=ON')
    cursor.close()
  async with engine.begin() as conn:
    await conn.run_sync(mapper_registry.metadata.drop_all)
    await conn.run_sync(ia_registry.metadata.drop_all)
    await conn.run_sync(outbox_mapper_registry.metadata.drop_all)

    await conn.run_sync(mapper_registry.metadata.create_all)
    await conn.run_sync(ia_registry.metadata.create_all)
    await conn.run_sync(outbox_mapper_registry.metadata.create_all)

  async with aiosqlite.connect(DB_PATH) as db:
    await db.execute(product_category_closure_query)

  await insert_data()


if __name__ == '__main__':
  asyncio.run(reset_db())