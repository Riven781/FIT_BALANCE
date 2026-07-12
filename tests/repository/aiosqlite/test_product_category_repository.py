import pytest

from api.repository.aiosqlite.product_category import ProductCategoryRepository

async def insert_categories(db):
  cursor = await db.execute("""
    INSERT INTO ProductCategory VALUES
      (1, "Produkty", NULL),
      (2, "Roślinne", 1),
      (3, "Zwierzęce", 1),
      (4, "Schab", 3),
      (5, "Boczek", 3),
      (6, "Tofu", 2),
      (7, "Groszek", 2),
      (8, "Groszek Zielony", 7),
      (9, "Boczek Pikantny", 5);
  """)
  await db.commit()
  await cursor.close()


@pytest.mark.asyncio
async def test_get_all(db):
  await insert_categories(db)
  repo = ProductCategoryRepository(db)
  categories = await repo.get_all()
  assert len(categories) == 9
  assert {'id' : 1, 'name': 'Produkty', 'parent_id' : None} in categories
  assert {'id' : 2, 'name': 'Roślinne', 'parent_id' : 1} in categories
  assert {'id' : 3, 'name': 'Zwierzęce', 'parent_id' : 1} in categories
  assert {'id' : 4, 'name': 'Schab', 'parent_id' : 3} in categories
  assert {'id' : 5, 'name': 'Boczek', 'parent_id' : 3} in categories
  assert {'id' : 6, 'name': 'Tofu', 'parent_id' : 2} in categories
  assert {'id' : 7, 'name': 'Groszek', 'parent_id' : 2} in categories
  assert {'id' : 8, 'name': 'Groszek Zielony', 'parent_id' : 7} in categories
  assert {'id' : 9, 'name': 'Boczek Pikantny', 'parent_id' : 5} in categories


@pytest.mark.asyncio
async def test_get_all_empty_table(db):
  repo = ProductCategoryRepository(db)
  categories = await repo.get_all()
  assert len(categories) == 0
