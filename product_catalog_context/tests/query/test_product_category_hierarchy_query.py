from aiosqlite import cursor
import pytest
from dataclasses import asdict

from product_catalog_context.infrastructure.aiosqlite_queries.category_hierarchy import ProductCategoryHierarchyQueries

async def insert_categories(db):
  cursor = await db.executescript("""

    INSERT INTO ProductCategoryHierarchy (id, status) VALUES
        (1, "ACTIVE");

    INSERT INTO ProductCategoryNode (id, name, parent_id, hierarchy_id) VALUES
      (1, "Produkty", NULL, 1),
      (2, "Roślinne", 1, 1),
      (3, "Zwierzęce", 1, 1),
      (4, "Schab", 3, 1),
      (5, "Boczek", 3, 1),
      (6, "Tofu", 2, 1),
      (7, "Groszek", 2, 1),
      (8, "Groszek Zielony", 7, 1),
      (9, "Boczek Pikantny", 5, 1);
                            
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
      (7, 7, 0),
      (8, 8, 0),
      (7, 8, 1),
      (2, 8, 2),
      (1, 8, 3),
      (9, 9, 0),
      (5, 9, 1),
      (3, 9, 2),
      (1, 9, 3);
  """)
  await db.commit()
  await cursor.close()

@pytest.mark.asyncio
async def test_get_by_supercategory_tree_with_depth_3(db):
  await insert_categories(db)
  repo = ProductCategoryHierarchyQueries(db)
  categories = await repo.get_by_supercategory(1)
  
  assert asdict(categories) == {'id': 1, 'name': 'Produkty', 'subcategories': [
      {
        'id': 2, 'name': 'Roślinne', 'subcategories' : [
          {'id': 6, 'name': 'Tofu', 'subcategories': []}, {'id': 7, 'name': 'Groszek', 'subcategories': [{'id': 8, 'name': 'Groszek Zielony', 'subcategories': []}]}
        ]
      },
      {
        'id' : 3, 'name': 'Zwierzęce', 'subcategories': [
          {'id': 4, 'name': 'Schab', 'subcategories': []}, {'id': 5, 'name': 'Boczek', 'subcategories': [{'id': 9, 'name': 'Boczek Pikantny', 'subcategories': []}]}
        ]
      }
    ]}
  
@pytest.mark.asyncio
async def test_get_by_supercategory_tree_with_depth_2(db):
  await insert_categories(db)
  repo = ProductCategoryHierarchyQueries(db)
  categories = await repo.get_by_supercategory(2)
  assert asdict(categories) == {'id': 2, 'name': 'Roślinne', 'subcategories' : [
        {'id': 6, 'name': 'Tofu', 'subcategories': []}, {'id': 7, 'name': 'Groszek', 'subcategories': [{'id': 8, 'name': 'Groszek Zielony', 'subcategories': []}]}
      ]
    }


@pytest.mark.asyncio
async def test_get_by_supercategory_tree_with_depth_1(db):
  await insert_categories(db)
  repo = ProductCategoryHierarchyQueries(db)
  categories = await repo.get_by_supercategory(7)
  assert asdict(categories) == {'id': 7, 'name': 'Groszek', 'subcategories' : [
        {'id': 8, 'name': 'Groszek Zielony', 'subcategories': []}
      ]
    }
  
@pytest.mark.asyncio
async def test_get_by_supercategory_tree_with_depth_0(db):
  await insert_categories(db)
  repo = ProductCategoryHierarchyQueries(db)
  categories = await repo.get_by_supercategory(6)
  assert asdict(categories) == {'id': 6, 'name': 'Tofu', 'subcategories': []}
     
@pytest.mark.asyncio
async def test_get_by_supercategory_not_existing_supercategory_id(db):
  await insert_categories(db)
  repo = ProductCategoryHierarchyQueries(db)
  categories = await repo.get_by_supercategory(100)
  assert categories == None


async def insert_categories_2_trees(db):
  cursor = await db.executescript("""
    INSERT INTO ProductCategoryHierarchy (id, status) VALUES
      (1, "ACTIVE");

    INSERT INTO ProductCategoryNode (id, name, parent_id, hierarchy_id) VALUES
      (2, "Roślinne", NULL, 1),
      (3, "Zwierzęce", NULL, 1),
      (4, "Schab", 3, 1),
      (5, "Boczek", 3, 1),
      (6, "Tofu", 2, 1),
      (7, "Groszek", 2, 1);
                            
    INSERT INTO ProductCategoryClosure VALUES
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
async def test_get_by_supercategory_2_trees_tree_with_depth_1(db):
  await insert_categories_2_trees(db)
  repo = ProductCategoryHierarchyQueries(db)
  categories = await repo.get_by_supercategory(2)
  assert asdict(categories) == {'id': 2, 'name': 'Roślinne', 'subcategories' : [
        {'id': 6, 'name': 'Tofu', 'subcategories': []}, {'id': 7, 'name': 'Groszek', 'subcategories': []}
      ]
    }

@pytest.mark.asyncio
async def test_get_by_supercategory_2_trees_tree_with_depth_0(db):
  await insert_categories_2_trees(db)
  repo = ProductCategoryHierarchyQueries(db)
  categories = await repo.get_by_supercategory(6)
  assert asdict(categories) == {'id': 6, 'name': 'Tofu', 'subcategories': []}

@pytest.mark.asyncio
async def test_get_tree_with_depth_3(db):
  await insert_categories(db)
  repo = ProductCategoryHierarchyQueries(db)
  categories = await repo.get()
  assert len(categories) == 1
  assert asdict(categories[0]) == {'id': 1, 'name': 'Produkty', 'subcategories': [
      {
        'id': 2, 'name': 'Roślinne', 'subcategories' : [
          {'id': 6, 'name': 'Tofu', 'subcategories': []}, {'id': 7, 'name': 'Groszek', 'subcategories': [{'id': 8, 'name': 'Groszek Zielony', 'subcategories': []}]}
        ]
      },
      {
        'id' : 3, 'name': 'Zwierzęce', 'subcategories': [
          {'id': 4, 'name': 'Schab', 'subcategories': []}, {'id': 5, 'name': 'Boczek', 'subcategories': [{'id': 9, 'name': 'Boczek Pikantny', 'subcategories': []}]}
        ]
      }
    ]}
  

@pytest.mark.asyncio
async def test_get_tree_many_trees_with_depth_2(db):
  await insert_categories_2_trees(db)
  repo = ProductCategoryHierarchyQueries(db)
  categories = await repo.get()
  print(categories)
  assert len(categories) == 2
  assert asdict(categories[0]) == {
        'id': 2, 'name': 'Roślinne', 'subcategories' : [
          {'id': 6, 'name': 'Tofu', 'subcategories': []}, {'id': 7, 'name': 'Groszek', 'subcategories': []}
        ]
      }

  assert asdict(categories[1]) == {
        'id' : 3, 'name': 'Zwierzęce', 'subcategories': [
          {'id': 4, 'name': 'Schab', 'subcategories': []}, {'id': 5, 'name': 'Boczek', 'subcategories': []}
        ]
      }

