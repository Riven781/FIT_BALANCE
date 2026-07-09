
from aiosqlite import cursor
import pytest

from api.repository.aiosqlite.product_category import ProductCategoryRepository
from api.repository.errors.errors import UniqueViolationError
from api.schemas.product_category import ProductCategoryCreate, ProductCategoryUpdate

async def insert_categories(db):
  cursor = await db.executescript("""
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
      (9, 9, 9),
      (5, 9, 1),
      (3, 9, 2),
      (1, 9, 3);
  """)
  await db.commit()
  await cursor.close()

@pytest.mark.asyncio
async def test_get_by_supercategory_tree_with_depth_3(db):
  await insert_categories(db)
  repo = ProductCategoryRepository(db)
  categories = await repo.get_by_supercategory(1)
  assert categories.model_dump() == {'id': 1, 'name': 'Produkty', 'subcategories': [
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
  repo = ProductCategoryRepository(db)
  categories = await repo.get_by_supercategory(2)
  assert categories.model_dump() == {'id': 2, 'name': 'Roślinne', 'subcategories' : [
        {'id': 6, 'name': 'Tofu', 'subcategories': []}, {'id': 7, 'name': 'Groszek', 'subcategories': [{'id': 8, 'name': 'Groszek Zielony', 'subcategories': []}]}
      ]
    }


@pytest.mark.asyncio
async def test_get_by_supercategory_tree_with_depth_1(db):
  await insert_categories(db)
  repo = ProductCategoryRepository(db)
  categories = await repo.get_by_supercategory(7)
  assert categories.model_dump() == {'id': 7, 'name': 'Groszek', 'subcategories' : [
        {'id': 8, 'name': 'Groszek Zielony', 'subcategories': []}
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
async def test_get_all_tree_with_depth_3(db):
  await insert_categories(db)
  repo = ProductCategoryRepository(db)
  categories = await repo.get_all()
  assert len(categories) == 1
  assert categories[0].model_dump() == {'id': 1, 'name': 'Produkty', 'subcategories': [
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
  product_category_data = ProductCategoryCreate(name= 'Groszek Zielolny Meksykański', supercategory_id= 8)
  await repo.insert(product_category_data)
  async with db.execute("SELECT * FROM ProductCategoryClosure WHERE subcategory_id=?", (10,)) as cursor:
    closure = await cursor.fetchall()
  closure_dict = [dict(c) for c in closure]

  assert len(closure) == 5
  assert {'supercategory_id': 10, 'subcategory_id': 10, 'depth': 0} in closure_dict
  assert {'supercategory_id': 1, 'subcategory_id': 10, 'depth': 4} in closure_dict
  assert {'supercategory_id': 2, 'subcategory_id': 10, 'depth': 3} in closure_dict
  assert {'supercategory_id': 7, 'subcategory_id': 10, 'depth': 2} in closure_dict
  assert {'supercategory_id': 8, 'subcategory_id': 10, 'depth': 1} in closure_dict

  async with db.execute("SELECT * FROM ProductCategory WHERE id=?", (10,)) as cursor:
    closure = await cursor.fetchall()
  assert len(closure) == 1
  product_category = closure[0]
  assert product_category['parent_id'] == 8
  assert product_category['name'] == 'Groszek Zielolny Meksykański'

@pytest.mark.asyncio
async def test_insert_first_level_node_as_parent(db):
  await insert_categories(db)
  repo = ProductCategoryRepository(db)
  product_category_data = ProductCategoryCreate(name= 'Jabłko', supercategory_id= 2)
  await repo.insert(product_category_data)
  async with db.execute("SELECT * FROM ProductCategoryClosure WHERE subcategory_id=?", (10,)) as cursor:
    closure = await cursor.fetchall()
  closure_dict = [dict(c) for c in closure]

  assert len(closure) == 3
  assert {'supercategory_id': 10, 'subcategory_id': 10, 'depth': 0} in closure_dict
  assert {'supercategory_id': 1, 'subcategory_id': 10, 'depth': 2} in closure_dict
  assert {'supercategory_id': 2, 'subcategory_id': 10, 'depth': 1} in closure_dict

  async with db.execute("SELECT * FROM ProductCategory WHERE id=?", (10,)) as cursor:
    closure = await cursor.fetchall()
  assert len(closure) == 1
  product_category = closure[0]
  assert product_category['parent_id'] == 2
  assert product_category['name'] == 'Jabłko'

@pytest.mark.asyncio
async def test_insert_second_level_node_as_parent(db):
  await insert_categories(db)
  repo = ProductCategoryRepository(db)
  product_category_data = ProductCategoryCreate(name= 'Groszek Biały', supercategory_id= 7)
  await repo.insert(product_category_data)
  async with db.execute("SELECT * FROM ProductCategoryClosure WHERE subcategory_id=?", (10,)) as cursor:
    closure = await cursor.fetchall()
  closure_dict = [dict(c) for c in closure]

  assert len(closure) == 4
  assert {'supercategory_id': 10, 'subcategory_id': 10, 'depth': 0} in closure_dict
  assert {'supercategory_id': 1, 'subcategory_id': 10, 'depth': 3} in closure_dict
  assert {'supercategory_id': 2, 'subcategory_id': 10, 'depth': 2} in closure_dict
  assert {'supercategory_id': 7, 'subcategory_id': 10, 'depth': 1} in closure_dict


  async with db.execute("SELECT * FROM ProductCategory WHERE id=?", (10,)) as cursor:
    closure = await cursor.fetchall()
  assert len(closure) == 1
  product_category = closure[0]
  assert product_category['parent_id'] == 7
  assert product_category['name'] == 'Groszek Biały'

@pytest.mark.asyncio
async def test_insert_root_as_parent(db):
  await insert_categories(db)
  repo = ProductCategoryRepository(db)
  product_category_data = ProductCategoryCreate(name= 'Mieszane', supercategory_id=1)
  await repo.insert(product_category_data)
  async with db.execute("SELECT * FROM ProductCategoryClosure WHERE subcategory_id=?", (10,)) as cursor:
    closure = await cursor.fetchall()
  closure_dict = [dict(c) for c in closure]

  assert len(closure) == 2
  assert {'supercategory_id': 10, 'subcategory_id': 10, 'depth': 0} in closure_dict
  assert {'supercategory_id': 1, 'subcategory_id': 10, 'depth': 1} in closure_dict

  async with db.execute("SELECT * FROM ProductCategory WHERE id=?", (10,)) as cursor:
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
  async with db.execute("SELECT * FROM ProductCategoryClosure WHERE subcategory_id=?", (10,)) as cursor:
    closure = await cursor.fetchall()
  closure_dict = [dict(c) for c in closure]

  assert len(closure) == 1
  assert {'supercategory_id': 10, 'subcategory_id': 10, 'depth': 0} in closure_dict

  async with db.execute("SELECT * FROM ProductCategory WHERE id=?", (10,)) as cursor:
    closure = await cursor.fetchall()
  assert len(closure) == 1
  product_category = closure[0]
  assert product_category['parent_id'] is None
  assert product_category['name'] == 'Produkty Archiwalne'

@pytest.mark.asyncio
async def test_insert_first_level_node_as_parent_with_one_child_that_has_own_child(db):
  await insert_categories(db)
  repo = ProductCategoryRepository(db)
  product_category_data = ProductCategoryCreate(name= 'Zielone', supercategory_id= 2, subcategories_id=[7])
  await repo.insert(product_category_data)
  async with db.execute("SELECT * FROM ProductCategoryClosure") as cursor:
    closure = await cursor.fetchall()
  closure_dict = [dict(c) for c in closure]

  assert {'supercategory_id': 10, 'subcategory_id': 10, 'depth': 0} in closure_dict
  assert {'supercategory_id': 1, 'subcategory_id': 10, 'depth': 2} in closure_dict
  assert {'supercategory_id': 2, 'subcategory_id': 10, 'depth': 1} in closure_dict

  assert {'supercategory_id': 10, 'subcategory_id': 7, 'depth': 1} in closure_dict
  assert {'supercategory_id': 10, 'subcategory_id': 8, 'depth': 2} in closure_dict

  assert {'supercategory_id': 1, 'subcategory_id': 7, 'depth': 3} in closure_dict
  assert {'supercategory_id': 1, 'subcategory_id': 8, 'depth': 4} in closure_dict
  assert {'supercategory_id': 2, 'subcategory_id': 7, 'depth': 2} in closure_dict
  assert {'supercategory_id': 2, 'subcategory_id': 8, 'depth': 3} in closure_dict
  assert {'supercategory_id': 1, 'subcategory_id': 6, 'depth': 2} in closure_dict
  assert {'supercategory_id': 2, 'subcategory_id': 6, 'depth': 1} in closure_dict

  assert {'supercategory_id': 10, 'subcategory_id': 6, 'depth': 1} not in closure_dict

  async with db.execute("SELECT * FROM ProductCategory WHERE id=?", (10,)) as cursor:
    category_list = await cursor.fetchall()
  assert len(category_list) == 1
  product_category = category_list[0]
  assert product_category['parent_id'] == 2
  assert product_category['name'] == 'Zielone'

  async with db.execute("SELECT * FROM ProductCategory ") as cursor:
    category_list = await cursor.fetchall()
  category_dict = [dict(c) for c in category_list]

  #print(category_dict)
  assert {'id':7, "name": "Groszek", "parent_id": 10} in category_dict
  assert {'id':6, "name": "Tofu", "parent_id": 2} in category_dict



@pytest.mark.asyncio
async def test_insert_first_level_node_as_parent_with_two_children(db):
  await insert_categories(db)
  repo = ProductCategoryRepository(db)
  product_category_data = ProductCategoryCreate(name= 'Zielone', supercategory_id= 2, subcategories_id=[7,6])
  await repo.insert(product_category_data)
  async with db.execute("SELECT * FROM ProductCategoryClosure") as cursor:
    closure = await cursor.fetchall()
  closure_dict = [dict(c) for c in closure]

  assert {'supercategory_id': 10, 'subcategory_id': 10, 'depth': 0} in closure_dict
  assert {'supercategory_id': 1, 'subcategory_id': 10, 'depth': 2} in closure_dict
  assert {'supercategory_id': 2, 'subcategory_id': 10, 'depth': 1} in closure_dict

  assert {'supercategory_id': 10, 'subcategory_id': 7, 'depth': 1} in closure_dict
  assert {'supercategory_id': 10, 'subcategory_id': 6, 'depth': 1} in closure_dict
  assert {'supercategory_id': 10, 'subcategory_id': 8, 'depth': 2} in closure_dict
  assert {'supercategory_id': 7, 'subcategory_id': 8, 'depth': 1} in closure_dict #it doesnt change

  assert {'supercategory_id': 1, 'subcategory_id': 7, 'depth': 3} in closure_dict
  assert {'supercategory_id': 2, 'subcategory_id': 7, 'depth': 2} in closure_dict
  assert {'supercategory_id': 1, 'subcategory_id': 6, 'depth': 3} in closure_dict
  assert {'supercategory_id': 2, 'subcategory_id': 6, 'depth': 2} in closure_dict
  assert {'supercategory_id': 1, 'subcategory_id': 8, 'depth': 4} in closure_dict
  assert {'supercategory_id': 2, 'subcategory_id': 8, 'depth': 3} in closure_dict

  async with db.execute("SELECT * FROM ProductCategory WHERE id=?", (10,)) as cursor:
    category_list = await cursor.fetchall()
  assert len(category_list) == 1
  product_category = category_list[0]
  assert product_category['parent_id'] == 2
  assert product_category['name'] == 'Zielone'

  async with db.execute("SELECT * FROM ProductCategory ") as cursor:
    category_list = await cursor.fetchall()
  category_dict = [dict(c) for c in category_list]

  #print(category_dict)
  assert {'id':7, "name": "Groszek", "parent_id": 10} in category_dict
  assert {'id':6, "name": "Tofu", "parent_id": 10} in category_dict


@pytest.mark.asyncio
async def test_insert_first_level_node_as_parent_adopt_all_child_subcategories(db):
  await insert_categories(db)
  repo = ProductCategoryRepository(db)
  product_category_data = ProductCategoryCreate(name= 'Zielone', supercategory_id= 2)
  await repo.insert(product_category_data, adopt_subcategories=True)
  async with db.execute("SELECT * FROM ProductCategoryClosure") as cursor:
    closure = await cursor.fetchall()
  closure_dict = [dict(c) for c in closure]

  assert {'supercategory_id': 10, 'subcategory_id': 10, 'depth': 0} in closure_dict
  assert {'supercategory_id': 1, 'subcategory_id': 10, 'depth': 2} in closure_dict
  assert {'supercategory_id': 2, 'subcategory_id': 10, 'depth': 1} in closure_dict

  assert {'supercategory_id': 10, 'subcategory_id': 7, 'depth': 1} in closure_dict
  assert {'supercategory_id': 10, 'subcategory_id': 6, 'depth': 1} in closure_dict
  assert {'supercategory_id': 10, 'subcategory_id': 8, 'depth': 2} in closure_dict
  assert {'supercategory_id': 7, 'subcategory_id': 8, 'depth': 1} in closure_dict #it doesnt change

  assert {'supercategory_id': 1, 'subcategory_id': 7, 'depth': 3} in closure_dict
  assert {'supercategory_id': 2, 'subcategory_id': 7, 'depth': 2} in closure_dict
  assert {'supercategory_id': 1, 'subcategory_id': 6, 'depth': 3} in closure_dict
  assert {'supercategory_id': 2, 'subcategory_id': 6, 'depth': 2} in closure_dict
  assert {'supercategory_id': 1, 'subcategory_id': 8, 'depth': 4} in closure_dict
  assert {'supercategory_id': 2, 'subcategory_id': 8, 'depth': 3} in closure_dict

  async with db.execute("SELECT * FROM ProductCategory WHERE id=?", (10,)) as cursor:
    category_list = await cursor.fetchall()
  assert len(category_list) == 1
  product_category = category_list[0]
  assert product_category['parent_id'] == 2
  assert product_category['name'] == 'Zielone'

  async with db.execute("SELECT * FROM ProductCategory ") as cursor:
    category_list = await cursor.fetchall()
  category_dict = [dict(c) for c in category_list]

  assert {'id':7, "name": "Groszek", "parent_id": 10} in category_dict
  assert {'id':6, "name": "Tofu", "parent_id": 10} in category_dict

@pytest.mark.asyncio
async def test_insert_second_level_node_as_parent_adopt_all_child_subcategories(db):
  await insert_categories(db)
  repo = ProductCategoryRepository(db)
  product_category_data = ProductCategoryCreate(name= 'Groszek Polski', supercategory_id= 7)
  await repo.insert(product_category_data, adopt_subcategories=True)
  async with db.execute("SELECT * FROM ProductCategoryClosure") as cursor:
    closure = await cursor.fetchall()
  closure_dict = [dict(c) for c in closure]

  assert {'supercategory_id': 10, 'subcategory_id': 10, 'depth': 0} in closure_dict
  assert {'supercategory_id': 1, 'subcategory_id': 10, 'depth': 3} in closure_dict
  assert {'supercategory_id': 2, 'subcategory_id': 10, 'depth': 2} in closure_dict

  assert {'supercategory_id': 7, 'subcategory_id': 10, 'depth': 1} in closure_dict

  assert {'supercategory_id': 10, 'subcategory_id': 8, 'depth': 1} in closure_dict
  
  assert {'supercategory_id': 7, 'subcategory_id': 8, 'depth': 2} in closure_dict

  assert {'supercategory_id': 1, 'subcategory_id': 7, 'depth': 2} in closure_dict
 

  async with db.execute("SELECT * FROM ProductCategory WHERE id=?", (10,)) as cursor:
    category_list = await cursor.fetchall()
  assert len(category_list) == 1
  product_category = category_list[0]
  assert product_category['parent_id'] == 7
  assert product_category['name'] == 'Groszek Polski'

  async with db.execute("SELECT * FROM ProductCategory ") as cursor:
    category_list = await cursor.fetchall()
  category_dict = [dict(c) for c in category_list]

  assert {'id':8, "name": "Groszek Zielony", "parent_id": 10} in category_dict
  assert {'id':6, "name": "Tofu", "parent_id": 2} in category_dict

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


@pytest.mark.asyncio
async def test_delete_leaf_category_with_subcategories_option(db):
  await insert_categories(db)
  repo = ProductCategoryRepository(db)
  count = await repo.delete(8, with_subcategories=True)
  assert count == 1
  async with db.execute("SELECT * FROM ProductCategoryClosure") as cursor:
    closure = await cursor.fetchall()
  closure_dict = [dict(c) for c in closure]
  assert {'supercategory_id': 8, 'subcategory_id': 8, 'depth': 0} not in closure_dict
  assert {'supercategory_id': 1, 'subcategory_id': 8, 'depth': 3} not in closure_dict
  assert {'supercategory_id': 2, 'subcategory_id': 8, 'depth': 2} not in closure_dict
  assert {'supercategory_id': 7, 'subcategory_id': 8, 'depth': 1} not in closure_dict



@pytest.mark.asyncio
async def test_delete_first_level_category_with_subcategories_option(db):
  await insert_categories(db)
  repo = ProductCategoryRepository(db)
  count = await repo.delete(2, with_subcategories=True)
  assert count == 4
  async with db.execute("SELECT * FROM ProductCategoryClosure") as cursor:
    closure = await cursor.fetchall()
  closure_dict = [dict(c) for c in closure]
  assert {'supercategory_id': 2, 'subcategory_id': 2, 'depth': 0} not in closure_dict
  assert {'supercategory_id': 1, 'subcategory_id': 2, 'depth': 1} not in closure_dict
  assert {'supercategory_id': 6, 'subcategory_id': 6, 'depth': 0} not in closure_dict
  assert {'supercategory_id': 1, 'subcategory_id': 6, 'depth': 2} not in closure_dict
  assert {'supercategory_id': 2, 'subcategory_id': 6, 'depth': 1} not in closure_dict
  assert {'supercategory_id': 7, 'subcategory_id': 7, 'depth': 0} not in closure_dict
  assert {'supercategory_id': 1, 'subcategory_id': 7, 'depth': 2} not in closure_dict
  assert {'supercategory_id': 2, 'subcategory_id': 7, 'depth': 1} not in closure_dict
  assert {'supercategory_id': 8, 'subcategory_id': 8, 'depth': 0} not in closure_dict
  assert {'supercategory_id': 1, 'subcategory_id': 8, 'depth': 3} not in closure_dict
  assert {'supercategory_id': 2, 'subcategory_id': 8, 'depth': 2} not in closure_dict
  assert {'supercategory_id': 7, 'subcategory_id': 8, 'depth': 1} not in closure_dict


@pytest.mark.asyncio
async def test_delete_second_level_category_with_subcategories_option(db):
  await insert_categories(db)
  repo = ProductCategoryRepository(db)
  count = await repo.delete(7, with_subcategories=True)
  assert count == 2
  async with db.execute("SELECT * FROM ProductCategoryClosure") as cursor:
    closure = await cursor.fetchall()
  closure_dict = [dict(c) for c in closure]
  assert {'supercategory_id': 7, 'subcategory_id': 7, 'depth': 0} not in closure_dict
  assert {'supercategory_id': 1, 'subcategory_id': 7, 'depth': 2} not in closure_dict
  assert {'supercategory_id': 8, 'subcategory_id': 8, 'depth': 0} not in closure_dict
  assert {'supercategory_id': 1, 'subcategory_id': 8, 'depth': 3} not in closure_dict
  assert {'supercategory_id': 2, 'subcategory_id': 8, 'depth': 2} not in closure_dict
  assert {'supercategory_id': 7, 'subcategory_id': 8, 'depth': 1} not in closure_dict
  assert {'supercategory_id': 8, 'subcategory_id': 8, 'depth': 0} not in closure_dict
  

@pytest.mark.asyncio
async def test_delete_root_category_with_subcategories_option(db):
  await insert_categories(db)
  repo = ProductCategoryRepository(db)
  count = await repo.delete(1, with_subcategories=True)
  assert count == 9
  async with db.execute("SELECT * FROM ProductCategoryClosure") as cursor:
    closure = await cursor.fetchall()
  closure_dict = [dict(c) for c in closure]
  assert len(closure_dict) == 0


@pytest.mark.asyncio
async def test_delete_leaf_category(db):
  await insert_categories(db)
  repo = ProductCategoryRepository(db)
  count = await repo.delete(8)
  assert count == 1
  async with db.execute("SELECT * FROM ProductCategoryClosure") as cursor:
    closure = await cursor.fetchall()
  closure_dict = [dict(c) for c in closure]
  assert {'supercategory_id': 8, 'subcategory_id': 8, 'depth': 0} not in closure_dict
  assert {'supercategory_id': 1, 'subcategory_id': 8, 'depth': 3} not in closure_dict
  assert {'supercategory_id': 2, 'subcategory_id': 8, 'depth': 2} not in closure_dict
  assert {'supercategory_id': 7, 'subcategory_id': 8, 'depth': 1} not in closure_dict

@pytest.mark.asyncio
async def test_delete_first_level_category(db):
  await insert_categories(db)
  repo = ProductCategoryRepository(db)
  count = await repo.delete(2)
  assert count == 1
  async with db.execute("SELECT * FROM ProductCategoryClosure") as cursor:
    closure = await cursor.fetchall()
  closure_dict = [dict(c) for c in closure]
  print(closure_dict)
  assert {'supercategory_id': 2, 'subcategory_id': 2, 'depth': 0} not in closure_dict
  assert {'supercategory_id': 1, 'subcategory_id': 2, 'depth': 1} not in closure_dict
  assert {'supercategory_id': 2, 'subcategory_id': 6, 'depth': 1} not in closure_dict
  assert {'supercategory_id': 2, 'subcategory_id': 7, 'depth': 1} not in closure_dict
  assert {'supercategory_id': 2, 'subcategory_id': 8, 'depth': 2} not in closure_dict

  assert {'supercategory_id': 6, 'subcategory_id': 6, 'depth': 0} in closure_dict
  assert {'supercategory_id': 1, 'subcategory_id': 6, 'depth': 1} in closure_dict
  assert {'supercategory_id': 7, 'subcategory_id': 7, 'depth': 0} in closure_dict
  assert {'supercategory_id': 1, 'subcategory_id': 7, 'depth': 1} in closure_dict

  assert {'supercategory_id': 1, 'subcategory_id': 8, 'depth': 2} in closure_dict
  assert {'supercategory_id': 7, 'subcategory_id': 8, 'depth': 1} in closure_dict

  async with db.execute("SELECT * FROM ProductCategory") as cursor:
    categories = await cursor.fetchall()
  categories_dict = [dict(c) for c in categories]
  assert {'id' : 2, 'name' : "Roślinne", 'parent_id': 1} not in categories_dict

  assert {'id' : 3, 'name' : "Zwierzęce", 'parent_id': 1} in categories_dict
  assert {'id' : 4, 'name' : "Schab", 'parent_id': 3} in categories_dict
  
  assert {'id' : 6, 'name' : "Tofu", 'parent_id': 1} in categories_dict
  assert {'id' : 7, 'name' : "Groszek", 'parent_id': 1} in categories_dict

  assert {'id' : 8, 'name' : "Groszek Zielony", 'parent_id': 7} in categories_dict

@pytest.mark.asyncio
async def test_delete_second_level_category(db):
  await insert_categories(db)
  repo = ProductCategoryRepository(db)
  count = await repo.delete(7)
  assert count == 1
  async with db.execute("SELECT * FROM ProductCategoryClosure") as cursor:
    closure = await cursor.fetchall()
  closure_dict = [dict(c) for c in closure]
  print(closure_dict)
  assert {'supercategory_id': 7, 'subcategory_id': 7, 'depth': 0} not in closure_dict
  assert {'supercategory_id': 1, 'subcategory_id': 7, 'depth': 2} not in closure_dict
  assert {'supercategory_id': 2, 'subcategory_id': 7, 'depth': 1} not in closure_dict
  assert {'supercategory_id': 7, 'subcategory_id': 8, 'depth': 1} not in closure_dict

  assert {'supercategory_id': 1, 'subcategory_id': 8, 'depth': 2} in closure_dict
  assert {'supercategory_id': 2, 'subcategory_id': 8, 'depth': 1} in closure_dict
  assert {'supercategory_id': 8, 'subcategory_id': 8, 'depth': 0} in closure_dict



  async with db.execute("SELECT * FROM ProductCategory") as cursor:
    categories = await cursor.fetchall()
  categories_dict = [dict(c) for c in categories] 
  assert {'id' : 7, 'name' : "Groszek", 'parent_id': 2} not in categories_dict

  assert {'id' : 2, 'name' : "Roślinne", 'parent_id': 1} in categories_dict
  assert {'id' : 3, 'name' : "Zwierzęce", 'parent_id': 1} in categories_dict
  assert {'id' : 4, 'name' : "Schab", 'parent_id': 3} in categories_dict
  assert {'id' : 6, 'name' : "Tofu", 'parent_id': 2} in categories_dict
  assert {'id' : 8, 'name' : "Groszek Zielony", 'parent_id': 2} in categories_dict

@pytest.mark.asyncio
async def test_delete_root_category(db):
  await insert_categories(db)
  repo = ProductCategoryRepository(db)
  count = await repo.delete(1)
  assert count == 1
  async with db.execute("SELECT * FROM ProductCategoryClosure") as cursor:
    closure = await cursor.fetchall()
  closure_dict = [dict(c) for c in closure]
  assert len(closure_dict) == 16
  assert {'supercategory_id': 1, 'subcategory_id': 1, 'depth': 0} not in closure_dict
  assert {'supercategory_id': 1, 'subcategory_id': 2, 'depth': 1} not in closure_dict
  assert {'supercategory_id': 1, 'subcategory_id': 3, 'depth': 1} not in closure_dict
  assert {'supercategory_id': 1, 'subcategory_id': 4, 'depth': 2} not in closure_dict
  assert {'supercategory_id': 1, 'subcategory_id': 5, 'depth': 2} not in closure_dict

  async with db.execute("SELECT * FROM ProductCategory") as cursor:
    categories = await cursor.fetchall()
  categories_dict = [dict(c) for c in categories]
  assert {'id' : 1, 'name' : "Produkty", 'parent_id': None} not in categories_dict

  assert {'id' : 2, 'name' : "Roślinne", 'parent_id': None} in categories_dict
  assert {'id' : 3, 'name' : "Zwierzęce", 'parent_id': None} in categories_dict
  assert {'id' : 4, 'name' : "Schab", 'parent_id': 3} in categories_dict


