import pytest

from api.repository.aiosqlite.product_category import ProductCategoryRepository

async def insert_categories_and_products(db):
  cursor = await db.executescript("""
    INSERT INTO ProductCategory VALUES
      (1, "Produkty", NULL),
      (2, "Roślinne", 1),
      (3, "Zwierzęce", 1),
      (4, "Schab", 3),
      (5, "Boczek", 3),
      (6, "Tofu", 2),
      (7, "Groszek", 2);
                            
    INSERT INTO ProductCategoryClosure VALUES
      (1, 1, 0),
      (1, 2, 1),
      (1, 3, 1),
      (1, 4, 2),
      (1, 5, 2),
      (1, 6, 2),
      (1, 7, 2),
      (2, 2, 0),
      (2, 6, 1),
      (2, 7, 1),
      (3, 3, 0),
      (3, 4, 1),
      (3, 5, 1),
      (4, 4, 0),
      (5, 5, 0),
      (6, 6, 0),
      (7, 7, 0);
  """)
  await db.commit()
  await cursor.close()

@pytest.mark.asyncio
async def test_get_by_supercategory_tree_with_depth_2(db):
  await insert_categories_and_products(db)
  repo = ProductCategoryRepository(db)
  categories = await repo.get_by_supercategory(1)
  assert categories.model_dump() == {'id': 1, 'name': 'Produkty', 'subcategories': [
      {
        'id': 2, 'name': 'Roślinne', 'subcategories' : [
          {'id': 6, 'name': 'Tofu', 'subcategories': []}, {'id': 7, 'name': 'Groszek', 'subcategories': []}
        ]
      },
      {
        'id' : 3, 'name': 'Zwierzęce', 'subcategories': [
          {'id': 4, 'name': 'Schab', 'subcategories': []}, {'id': 5, 'name': 'Boczek', 'subcategories': []}
        ]
      }
    ]}
  
@pytest.mark.asyncio
async def test_get_by_supercategory_tree_with_depth_1(db):
  await insert_categories_and_products(db)
  repo = ProductCategoryRepository(db)
  categories = await repo.get_by_supercategory(2)
  assert categories.model_dump() == {'id': 2, 'name': 'Roślinne', 'subcategories' : [
        {'id': 6, 'name': 'Tofu', 'subcategories': []}, {'id': 7, 'name': 'Groszek', 'subcategories': []}
      ]
    }

@pytest.mark.asyncio
async def test_get_by_supercategory_tree_with_depth_0(db):
  await insert_categories_and_products(db)
  repo = ProductCategoryRepository(db)
  categories = await repo.get_by_supercategory(6)
  assert categories.model_dump() == {'id': 6, 'name': 'Tofu', 'subcategories': []}
     
@pytest.mark.asyncio
async def test_get_by_supercategory_not_existing_supercategory_id(db):
  await insert_categories_and_products(db)
  repo = ProductCategoryRepository(db)
  categories = await repo.get_by_supercategory(100)
  assert categories == None
