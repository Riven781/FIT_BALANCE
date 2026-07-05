
from aiosqlite import cursor
import pytest

from api.repository.aiosqlite.product_category import ProductCategoryRepository
from api.repository.errors.errors import UniqueViolationError
from api.schemas.product_category import ProductCategoryCreate

async def insert_categories(db):
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
  await insert_categories(db)
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
  await insert_categories(db)
  repo = ProductCategoryRepository(db)
  categories = await repo.get_by_supercategory(2)
  assert categories.model_dump() == {'id': 2, 'name': 'Roślinne', 'subcategories' : [
        {'id': 6, 'name': 'Tofu', 'subcategories': []}, {'id': 7, 'name': 'Groszek', 'subcategories': []}
      ]
    }

@pytest.mark.asyncio
async def test_get_by_supercategory_tree_with_depth_0(db):
  await insert_categories(db)
  repo = ProductCategoryRepository(db)
  categories = await repo.get_by_supercategory(6)
  assert categories.model_dump() == {'id': 6, 'name': 'Tofu', 'subcategories': []}
     
@pytest.mark.asyncio
async def test_get_by_supercategory_not_existing_supercategory_id(db):
  await insert_categories(db)
  repo = ProductCategoryRepository(db)
  categories = await repo.get_by_supercategory(100)
  assert categories == None


async def insert_categories_2_trees(db):
  cursor = await db.executescript("""
    INSERT INTO ProductCategory VALUES
      (2, "Roślinne", NULL),
      (3, "Zwierzęce", NULL),
      (4, "Schab", 3),
      (5, "Boczek", 3),
      (6, "Tofu", 2),
      (7, "Groszek", 2);
                            
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
  repo = ProductCategoryRepository(db)
  categories = await repo.get_by_supercategory(2)
  assert categories.model_dump() == {'id': 2, 'name': 'Roślinne', 'subcategories' : [
        {'id': 6, 'name': 'Tofu', 'subcategories': []}, {'id': 7, 'name': 'Groszek', 'subcategories': []}
      ]
    }

@pytest.mark.asyncio
async def test_get_by_supercategory_2_trees_tree_with_depth_0(db):
  await insert_categories_2_trees(db)
  repo = ProductCategoryRepository(db)
  categories = await repo.get_by_supercategory(6)
  assert categories.model_dump() == {'id': 6, 'name': 'Tofu', 'subcategories': []}

@pytest.mark.asyncio
async def test_get_all_tree_with_depth_2(db):
  await insert_categories(db)
  repo = ProductCategoryRepository(db)
  categories = await repo.get_all()
  assert len(categories) == 1
  assert categories[0].model_dump() == {'id': 1, 'name': 'Produkty', 'subcategories': [
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
async def test_get_all_tree_many_trees_with_depth_2(db):
  await insert_categories_2_trees(db)
  repo = ProductCategoryRepository(db)
  categories = await repo.get_all()
  print(categories)
  assert len(categories) == 2
  assert categories[0].model_dump() == {
        'id': 2, 'name': 'Roślinne', 'subcategories' : [
          {'id': 6, 'name': 'Tofu', 'subcategories': []}, {'id': 7, 'name': 'Groszek', 'subcategories': []}
        ]
      }

  assert categories[1].model_dump() == {
        'id' : 3, 'name': 'Zwierzęce', 'subcategories': [
          {'id': 4, 'name': 'Schab', 'subcategories': []}, {'id': 5, 'name': 'Boczek', 'subcategories': []}
        ]
      }

@pytest.mark.asyncio
async def test_insert_leaf_as_parent(db):
  await insert_categories(db)
  repo = ProductCategoryRepository(db)
  product_category_data = ProductCategoryCreate(name= 'Zielony Groszek', supercategory_id= 7)
  await repo.insert(product_category_data)
  async with db.execute("SELECT * FROM ProductCategoryClosure WHERE subcategory_id=?", (8,)) as cursor:
    closure = await cursor.fetchall()
  closure_dict = [dict(c) for c in closure]

  assert len(closure) == 4
  assert {'supercategory_id': 8, 'subcategory_id': 8, 'depth': 0} in closure_dict
  assert {'supercategory_id': 1, 'subcategory_id': 8, 'depth': 3} in closure_dict
  assert {'supercategory_id': 2, 'subcategory_id': 8, 'depth': 2} in closure_dict
  assert {'supercategory_id': 7, 'subcategory_id': 8, 'depth': 1} in closure_dict

  async with db.execute("SELECT * FROM ProductCategory WHERE id=?", (8,)) as cursor:
    closure = await cursor.fetchall()
  assert len(closure) == 1
  product_category = closure[0]
  assert product_category['parent_id'] == 7
  assert product_category['name'] == 'Zielony Groszek'

@pytest.mark.asyncio
async def test_insert_internal_node_as_parent(db):
  await insert_categories(db)
  repo = ProductCategoryRepository(db)
  product_category_data = ProductCategoryCreate(name= 'Jabłko', supercategory_id= 2)
  await repo.insert(product_category_data)
  async with db.execute("SELECT * FROM ProductCategoryClosure WHERE subcategory_id=?", (8,)) as cursor:
    closure = await cursor.fetchall()
  closure_dict = [dict(c) for c in closure]

  assert len(closure) == 3
  assert {'supercategory_id': 8, 'subcategory_id': 8, 'depth': 0} in closure_dict
  assert {'supercategory_id': 1, 'subcategory_id': 8, 'depth': 2} in closure_dict
  assert {'supercategory_id': 2, 'subcategory_id': 8, 'depth': 1} in closure_dict

  async with db.execute("SELECT * FROM ProductCategory WHERE id=?", (8,)) as cursor:
    closure = await cursor.fetchall()
  assert len(closure) == 1
  product_category = closure[0]
  assert product_category['parent_id'] == 2
  assert product_category['name'] == 'Jabłko'


@pytest.mark.asyncio
async def test_insert_internal_root_as_parent(db):
  await insert_categories(db)
  repo = ProductCategoryRepository(db)
  product_category_data = ProductCategoryCreate(name= 'Mieszane', supercategory_id=1)
  await repo.insert(product_category_data)
  async with db.execute("SELECT * FROM ProductCategoryClosure WHERE subcategory_id=?", (8,)) as cursor:
    closure = await cursor.fetchall()
  closure_dict = [dict(c) for c in closure]

  assert len(closure) == 2
  assert {'supercategory_id': 8, 'subcategory_id': 8, 'depth': 0} in closure_dict
  assert {'supercategory_id': 1, 'subcategory_id': 8, 'depth': 1} in closure_dict

  async with db.execute("SELECT * FROM ProductCategory WHERE id=?", (8,)) as cursor:
    closure = await cursor.fetchall()
  assert len(closure) == 1
  product_category = closure[0]
  assert product_category['parent_id'] == 1
  assert product_category['name'] == 'Mieszane'

@pytest.mark.asyncio
async def test_insert_without_parent(db):
  await insert_categories(db)
  repo = ProductCategoryRepository(db)
  product_category_data = ProductCategoryCreate(name= 'Produkty Archiwalne', supercategory_id=None)
  await repo.insert(product_category_data)
  async with db.execute("SELECT * FROM ProductCategoryClosure WHERE subcategory_id=?", (8,)) as cursor:
    closure = await cursor.fetchall()
  closure_dict = [dict(c) for c in closure]

  assert len(closure) == 1
  assert {'supercategory_id': 8, 'subcategory_id': 8, 'depth': 0} in closure_dict

  async with db.execute("SELECT * FROM ProductCategory WHERE id=?", (8,)) as cursor:
    closure = await cursor.fetchall()
  assert len(closure) == 1
  product_category = closure[0]
  assert product_category['parent_id'] is None
  assert product_category['name'] == 'Produkty Archiwalne'

@pytest.mark.asyncio
async def test_insert_internal_node_as_parent_with_one_child(db):
  await insert_categories(db)
  repo = ProductCategoryRepository(db)
  product_category_data = ProductCategoryCreate(name= 'Zielone', supercategory_id= 2, subcategories_id=[7])
  await repo.insert(product_category_data)
  async with db.execute("SELECT * FROM ProductCategoryClosure") as cursor:
    closure = await cursor.fetchall()
  closure_dict = [dict(c) for c in closure]

  assert {'supercategory_id': 8, 'subcategory_id': 8, 'depth': 0} in closure_dict
  assert {'supercategory_id': 1, 'subcategory_id': 8, 'depth': 2} in closure_dict
  assert {'supercategory_id': 2, 'subcategory_id': 8, 'depth': 1} in closure_dict

  assert {'supercategory_id': 8, 'subcategory_id': 7, 'depth': 1} in closure_dict

  assert {'supercategory_id': 1, 'subcategory_id': 7, 'depth': 3} in closure_dict
  assert {'supercategory_id': 2, 'subcategory_id': 7, 'depth': 2} in closure_dict
  assert {'supercategory_id': 1, 'subcategory_id': 6, 'depth': 2} in closure_dict
  assert {'supercategory_id': 2, 'subcategory_id': 6, 'depth': 1} in closure_dict

  async with db.execute("SELECT * FROM ProductCategory WHERE id=?", (8,)) as cursor:
    category_list = await cursor.fetchall()
  assert len(category_list) == 1
  product_category = category_list[0]
  assert product_category['parent_id'] == 2
  assert product_category['name'] == 'Zielone'

  async with db.execute("SELECT * FROM ProductCategory ") as cursor:
    category_list = await cursor.fetchall()
  category_dict = [dict(c) for c in category_list]

  #print(category_dict)
  assert {'id':7, "name": "Groszek", "parent_id": 8} in category_dict
  assert {'id':6, "name": "Tofu", "parent_id": 2} in category_dict



@pytest.mark.asyncio
async def test_insert_internal_node_as_parent_with_two_children(db):
  await insert_categories(db)
  repo = ProductCategoryRepository(db)
  product_category_data = ProductCategoryCreate(name= 'Zielone', supercategory_id= 2, subcategories_id=[7,6])
  await repo.insert(product_category_data)
  async with db.execute("SELECT * FROM ProductCategoryClosure") as cursor:
    closure = await cursor.fetchall()
  closure_dict = [dict(c) for c in closure]

  assert {'supercategory_id': 8, 'subcategory_id': 8, 'depth': 0} in closure_dict
  assert {'supercategory_id': 1, 'subcategory_id': 8, 'depth': 2} in closure_dict
  assert {'supercategory_id': 2, 'subcategory_id': 8, 'depth': 1} in closure_dict

  assert {'supercategory_id': 8, 'subcategory_id': 7, 'depth': 1} in closure_dict

  assert {'supercategory_id': 1, 'subcategory_id': 7, 'depth': 3} in closure_dict
  assert {'supercategory_id': 2, 'subcategory_id': 7, 'depth': 2} in closure_dict
  assert {'supercategory_id': 1, 'subcategory_id': 6, 'depth': 3} in closure_dict
  assert {'supercategory_id': 2, 'subcategory_id': 6, 'depth': 2} in closure_dict

  async with db.execute("SELECT * FROM ProductCategory WHERE id=?", (8,)) as cursor:
    category_list = await cursor.fetchall()
  assert len(category_list) == 1
  product_category = category_list[0]
  assert product_category['parent_id'] == 2
  assert product_category['name'] == 'Zielone'

  async with db.execute("SELECT * FROM ProductCategory ") as cursor:
    category_list = await cursor.fetchall()
  category_dict = [dict(c) for c in category_list]

  #print(category_dict)
  assert {'id':7, "name": "Groszek", "parent_id": 8} in category_dict
  assert {'id':6, "name": "Tofu", "parent_id": 8} in category_dict


@pytest.mark.asyncio
async def test_insert_internal_node_as_parent_adopt_all_child_subcategories(db):
  await insert_categories(db)
  repo = ProductCategoryRepository(db)
  product_category_data = ProductCategoryCreate(name= 'Zielone', supercategory_id= 2, should_adopt_all_subcategories=True)
  await repo.insert(product_category_data)
  async with db.execute("SELECT * FROM ProductCategoryClosure") as cursor:
    closure = await cursor.fetchall()
  closure_dict = [dict(c) for c in closure]

  assert {'supercategory_id': 8, 'subcategory_id': 8, 'depth': 0} in closure_dict
  assert {'supercategory_id': 1, 'subcategory_id': 8, 'depth': 2} in closure_dict
  assert {'supercategory_id': 2, 'subcategory_id': 8, 'depth': 1} in closure_dict

  assert {'supercategory_id': 8, 'subcategory_id': 7, 'depth': 1} in closure_dict

  assert {'supercategory_id': 1, 'subcategory_id': 7, 'depth': 3} in closure_dict
  assert {'supercategory_id': 2, 'subcategory_id': 7, 'depth': 2} in closure_dict
  assert {'supercategory_id': 1, 'subcategory_id': 6, 'depth': 3} in closure_dict
  assert {'supercategory_id': 2, 'subcategory_id': 6, 'depth': 2} in closure_dict

  async with db.execute("SELECT * FROM ProductCategory WHERE id=?", (8,)) as cursor:
    category_list = await cursor.fetchall()
  assert len(category_list) == 1
  product_category = category_list[0]
  assert product_category['parent_id'] == 2
  assert product_category['name'] == 'Zielone'

  async with db.execute("SELECT * FROM ProductCategory ") as cursor:
    category_list = await cursor.fetchall()
  category_dict = [dict(c) for c in category_list]

  #print(category_dict)
  assert {'id':7, "name": "Groszek", "parent_id": 8} in category_dict
  assert {'id':6, "name": "Tofu", "parent_id": 8} in category_dict

@pytest.mark.asyncio
async def test_insert_empty_db(db):
  repo = ProductCategoryRepository(db)
  product_category_data = ProductCategoryCreate(name= 'Produkt', supercategory_id=None)
  await repo.insert(product_category_data)
  async with db.execute("SELECT * FROM ProductCategoryClosure") as cursor:
    closure = await cursor.fetchall()
  closure_dict = [dict(c) for c in closure]

  assert len(closure_dict) == 1
  assert {'supercategory_id': 1, 'subcategory_id': 1, 'depth': 0} in closure_dict

  async with db.execute("SELECT * FROM ProductCategory WHERE id=?", (1,)) as cursor:
    category_list = await cursor.fetchall()
  assert len(category_list) == 1
  product_category = category_list[0]
  assert product_category['name'] == 'Produkt'


@pytest.mark.asyncio
async def test_insert_one_category_has_two_parents(db):
  await insert_categories(db)
  repo = ProductCategoryRepository(db)
  product_category_data = ProductCategoryCreate(name='Roślinnopodobne', supercategory_id=1, subcategories_id=[6])
  with pytest.raises(UniqueViolationError):
    await repo.insert(product_category_data)

