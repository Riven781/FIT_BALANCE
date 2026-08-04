import pytest

from product_catalog_context.infrastructure.aiosqlite_repository.product_category import ProductCategoryRepository
from product_catalog_context.infrastructure.aiosqlite_repository.errors.errors import ForeignKeyViolationError
from product_catalog_context.infrastructure.api.rest.schemas.product_category import ProductCategoryCreate, ProductCategoryUpdate

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


@pytest.mark.asyncio
async def test_delete_one_category_using_single_arg(db):
  await insert_categories(db)
  repo = ProductCategoryRepository(db)
  deleted_count = await repo.delete(2)
  assert deleted_count == 1
  categories = await repo.get_all()
  assert len(categories) == 8
  assert {'id' : 2, 'name': 'Roślinne', 'parent_id' : 1} not in categories

@pytest.mark.asyncio
async def test_delete_one_category_using_list_arg(db):
  await insert_categories(db)
  repo = ProductCategoryRepository(db)
  deleted_count = await repo.delete([2])
  assert deleted_count == 1
  categories = await repo.get_all()
  assert len(categories) == 8
  assert {'id' : 2, 'name': 'Roślinne', 'parent_id' : 1} not in categories

@pytest.mark.asyncio
async def test_delete_not_existing_category(db):
  await insert_categories(db)
  repo = ProductCategoryRepository(db)
  deleted_count = await repo.delete(20)
  assert deleted_count == 0
  categories = await repo.get_all()
  assert len(categories) == 9

@pytest.mark.asyncio
async def test_delete_not_existing_category_using_list_arg(db):
  await insert_categories(db)
  repo = ProductCategoryRepository(db)
  deleted_count = await repo.delete([2, 20])
  assert deleted_count == 1
  categories = await repo.get_all()
  assert len(categories) == 8

@pytest.mark.asyncio
async def test_delete_using_list_arg_empty_list(db):
  await insert_categories(db)
  repo = ProductCategoryRepository(db)
  deleted_count = await repo.delete([])
  assert deleted_count == 0
  categories = await repo.get_all()
  assert len(categories) == 9

@pytest.mark.asyncio
async def test_delete_two_categories(db):
  await insert_categories(db)
  repo = ProductCategoryRepository(db)
  deleted_count = await repo.delete([2, 4])
  assert deleted_count == 2
  categories = await repo.get_all()
  assert len(categories) == 7
  assert {'id' : 2, 'name': 'Roślinne', 'parent_id' : 1} not in categories
  assert {'id' : 7, 'name': 'Groszek', 'parent_id' : 2} not in categories

@pytest.mark.asyncio
async def test_insert_one_category(db):
  await insert_categories(db)
  repo = ProductCategoryRepository(db)
  category_id = await repo.insert(ProductCategoryCreate(name='Salceson', parent_id=3))
  assert category_id == 10
  categories = await repo.get_all()
  assert len(categories) == 10
  assert {'id' : 10, 'name': 'Salceson', 'parent_id' : 3} in categories

@pytest.mark.asyncio
async def test_insert_one_category_return_obj(db):
  await insert_categories(db)
  repo = ProductCategoryRepository(db)
  category = await repo.insert(ProductCategoryCreate(name='Salceson', parent_id=3), return_obj=True)
  assert category == {'id' : 10, 'name': 'Salceson', 'parent_id' : 3}
  categories = await repo.get_all()
  assert len(categories) == 10
  assert {'id' : 10, 'name': 'Salceson', 'parent_id' : 3} in categories

@pytest.mark.asyncio
async def test_insert_one_category_using_list_arg(db):
  await insert_categories(db)
  repo = ProductCategoryRepository(db)
  ids = await repo.insert([ProductCategoryCreate(name='Salceson', parent_id=3)])
  assert len(ids) == 1
  assert ids[0] == 10
  categories = await repo.get_all()
  assert len(categories) == 10
  assert {'id' : 10, 'name': 'Salceson', 'parent_id' : 3} in categories

@pytest.mark.asyncio
async def test_insert_two_categories(db):
  await insert_categories(db)
  repo = ProductCategoryRepository(db)
  categories = await repo.insert([ProductCategoryCreate(name='Salceson', parent_id=3), ProductCategoryCreate(name='Jabłko', parent_id=2)], return_obj=True)
  assert len(categories) == 2
  assert categories[0] == {'id' : 10, 'name': 'Salceson', 'parent_id' : 3}
  assert categories[1] == {'id' : 11, 'name': 'Jabłko', 'parent_id' : 2}
  categories = await repo.get_all()
  assert len(categories) == 11
  assert {'id' : 1, 'name': 'Produkty', 'parent_id' : None} in categories
  assert {'id' : 2, 'name': 'Roślinne', 'parent_id' : 1} in categories
  assert {'id' : 3, 'name': 'Zwierzęce', 'parent_id' : 1} in categories
  assert {'id' : 4, 'name': 'Schab', 'parent_id' : 3} in categories
  assert {'id' : 5, 'name': 'Boczek', 'parent_id' : 3} in categories
  assert {'id' : 6, 'name': 'Tofu', 'parent_id' : 2} in categories
  assert {'id' : 7, 'name': 'Groszek', 'parent_id' : 2} in categories
  assert {'id' : 8, 'name': 'Groszek Zielony', 'parent_id' : 7} in categories
  assert {'id' : 9, 'name': 'Boczek Pikantny', 'parent_id' : 5} in categories
  assert {'id' : 10, 'name': 'Salceson', 'parent_id' : 3} in categories
  assert {'id' : 11, 'name': 'Jabłko', 'parent_id' : 2} in categories

@pytest.mark.asyncio
async def test_insert_two_categories_without_return_obj(db):
  await insert_categories(db)
  repo = ProductCategoryRepository(db)
  categories = await repo.insert([ProductCategoryCreate(name='Salceson', parent_id=3), ProductCategoryCreate(name='Jabłko', parent_id=2)])
  assert len(categories) == 2
  assert categories[0] == 10
  assert categories[1] == 11
  categories = await repo.get_all()
  assert len(categories) == 11
  assert {'id' : 1, 'name': 'Produkty', 'parent_id' : None} in categories
  assert {'id' : 2, 'name': 'Roślinne', 'parent_id' : 1} in categories
  assert {'id' : 3, 'name': 'Zwierzęce', 'parent_id' : 1} in categories
  assert {'id' : 4, 'name': 'Schab', 'parent_id' : 3} in categories
  assert {'id' : 5, 'name': 'Boczek', 'parent_id' : 3} in categories
  assert {'id' : 6, 'name': 'Tofu', 'parent_id' : 2} in categories
  assert {'id' : 7, 'name': 'Groszek', 'parent_id' : 2} in categories
  assert {'id' : 8, 'name': 'Groszek Zielony', 'parent_id' : 7} in categories
  assert {'id' : 9, 'name': 'Boczek Pikantny', 'parent_id' : 5} in categories
  assert {'id' : 10, 'name': 'Salceson', 'parent_id' : 3} in categories
  assert {'id' : 11, 'name': 'Jabłko', 'parent_id' : 2} in categories


@pytest.mark.asyncio
async def test_update_category_rename(db):
  await insert_categories(db)
  repo = ProductCategoryRepository(db)
  count = await repo.update(2, ProductCategoryUpdate(name='Roślinnopodobne'))
  assert count == 1
  categories = await repo.get_all()
  assert len(categories) == 9
  assert {'id': 2, 'name': 'Roślinne', 'parent_id': 1} not in categories
  assert {'id': 2, 'name': 'Roślinnopodobne', 'parent_id': 1} in categories

@pytest.mark.asyncio
async def test_update_category_change_parent(db):
  await insert_categories(db)
  repo = ProductCategoryRepository(db)
  count = await repo.update(2, ProductCategoryUpdate(parent_id=5))
  assert count == 1
  categories = await repo.get_all()
  assert len(categories) == 9
  assert {'id': 2, 'name': 'Roślinne', 'parent_id': 1} not in categories
  assert {'id': 2, 'name': 'Roślinne', 'parent_id': 5} in categories


@pytest.mark.asyncio
async def test_update_category_set_not_existing_parent(db):
  await insert_categories(db)
  repo = ProductCategoryRepository(db)
  with pytest.raises(ForeignKeyViolationError):
    count = await repo.update(2, ProductCategoryUpdate(parent_id=500))


@pytest.mark.asyncio
async def test_update_category_rename_and_change_parent(db):
  await insert_categories(db)
  repo = ProductCategoryRepository(db)
  count = await repo.update(2, ProductCategoryUpdate(name='Roślinnopodobne', parent_id=5))
  assert count == 1
  categories = await repo.get_all()
  assert len(categories) == 9
  assert {'id': 2, 'name': 'Roślinne', 'parent_id': 1} not in categories
  assert {'id': 2, 'name': 'Roślinnopodobne', 'parent_id': 5} in categories

@pytest.mark.asyncio
async def test_update_two_categories_rename_and_change_parent(db):
  await insert_categories(db)
  repo = ProductCategoryRepository(db)
  count = await repo.update([2, 3], [ProductCategoryUpdate(name='Roślinnopodobne', parent_id=5), ProductCategoryUpdate(name='Zwierzęcopodobne', parent_id=6)])
  assert count == 2
  categories = await repo.get_all()
  assert len(categories) == 9
  assert {'id': 2, 'name': 'Roślinne', 'parent_id': 1} not in categories
  assert {'id': 2, 'name': 'Roślinnopodobne', 'parent_id': 5} in categories
  assert {'id' : 3, 'name': 'Zwierzęce', 'parent_id' : 1} not in categories
  assert {'id' : 3, 'name': 'Zwierzęcopodobne', 'parent_id' : 6} in categories

@pytest.mark.asyncio
async def test_update_one_category_rename_and_change_parent_using_list_arg(db):
  await insert_categories(db)
  repo = ProductCategoryRepository(db)
  count = await repo.update([2], [ProductCategoryUpdate(name='Roślinnopodobne', parent_id=5)])
  assert count == 1
  categories = await repo.get_all()
  assert len(categories) == 9
  assert {'id': 2, 'name': 'Roślinne', 'parent_id': 1} not in categories
  assert {'id': 2, 'name': 'Roślinnopodobne', 'parent_id': 5} in categories