
import pytest

from api.enums.product import SortBy
from api.repository.aiosqlite.product import ProductRepository
from api.repository.errors.errors import ForeignKeyViolationError, NotNullViolationError, RepositoryError, RepositoryIntegrityError, TypeViolationError, UniqueViolationError
from api.schemas.product import ProductBase, ProductCreate, ProductUpdate
from tests.schema import ProductTest, ProductTestStrKcal

async def insert_categories_and_products(db):
  cursor = await db.executescript("""
    INSERT INTO ProductCategory VALUES
      (1, "Produkty"),
      (2, "Roślinne"),
      (3, "Zwierzęce"),
      (4, "Schab"),
      (5, "Boczek");
                            
    INSERT INTO ProductCategoryClosure VALUES
      (1, 1, 0),
      (1, 2, 1),
      (1, 3, 1),
      (1, 4, 2),
      (1, 5, 2),
      (2, 2, 0),
      (3, 3, 0),
      (3, 4, 1),
      (3, 5, 1),
      (4, 4, 0),
      (5, 5, 0);
    
    INSERT INTO Product (id, name, brand, kcal, reference_amount, reference_unit, name_search_standard, category_id)
    VALUES 
    (1, "Schab Drogi", "Auchan", 300, 100, "g","schab drogi", 4),
    (2, "Schab Tani", "Rambert", 250, 100, "g", "schab tani", 4),
    (3, "Schab Średni", "XYZ", 400, 100, "g", "schab sredni", 4),

    (4, "Tofu", "XYZ", 300, 100, "g", "tofu", 2),
    (5, "Groszek", "ABC", 100, 100, "g", "groszek", 2),
                                                              
    (6, "Boczek Kaszubski", "WWW", 500, 100, "g", "boczek kaszubski", 5),
    (7, "Boczek Cielęcy", "YYY", 400, 100, "g", "boczek cielecy", 5),
    (8, "Raw Energy Baton kakaowy Bombus", "BB", 300, 100, "g", "raw energy baton kakaowy bombus", 2);
  """)

  await db.commit()
  await cursor.close()



async def insert_line(db):
  cursor = await db.execute("""
    INSERT INTO Product (name, brand, kcal, reference_unit, reference_amount)
    VALUES ("Karmel", "Auchan", 300, "g", 100);
    """
  )
  await db.commit()
  product_id = cursor.lastrowid
  await cursor.close()
  return product_id

@pytest.mark.asyncio
async def test_get_by_filters_names(db):
  await insert_categories_and_products(db)
  repo = ProductRepository(db)
  products = await repo.get_by_filters(names=['schab'])
  assert len(products) == 3

@pytest.mark.asyncio
async def test_get_by_filters_convert_polish_chars(db):
  await insert_categories_and_products(db)
  repo = ProductRepository(db)
  products = await repo.get_by_filters(names=['cielecy'])
  assert len(products) == 1

@pytest.mark.asyncio
async def test_get_by_filters_parts_of_words(db):
  await insert_categories_and_products(db)
  repo = ProductRepository(db)
  products = await repo.get_by_filters(names=['bo', 'kasz'])
  assert len(products) == 1

@pytest.mark.asyncio
async def test_get_by_filters_separted_parts_of_words(db):
  await insert_categories_and_products(db)
  repo = ProductRepository(db)
  products = await repo.get_by_filters(names=['bo', 'gro'])
  assert len(products) == 0 #boczek and groszek must be in one product name (together)

@pytest.mark.asyncio
async def test_get_by_filters_separted_parts_of_words_with_categories(db):
  await insert_categories_and_products(db)
  repo = ProductRepository(db)
  products = await repo.get_by_filters(names=['bo', 'gro'], category_id=5)
  assert len(products) == 0 #boczek and groszek must be in one product name (together)

@pytest.mark.asyncio
async def test_get_by_filters_part_of_words_in_middle(db):
  await insert_categories_and_products(db)
  repo = ProductRepository(db)
  products = await repo.get_by_filters(names=['czek'])
  assert len(products) == 0


@pytest.mark.asyncio
async def test_get_by_filters_category_empty_db(db):
  repo = ProductRepository(db)
  products = await repo.get_by_filters(category_id=10,sort_by=SortBy.KCAL, order="ASC")
  assert products == []


@pytest.mark.asyncio
async def test_get_by_filters_category_asc(db):
  await insert_categories_and_products(db)
  repo = ProductRepository(db)
  products = await repo.get_by_filters(category_id=4)
  assert len(products) == 3
  assert products[0].id == 2
  assert products[2].id == 3

@pytest.mark.asyncio
async def test_get_by_filters_category_desc(db):
  await insert_categories_and_products(db)
  repo = ProductRepository(db)
  products = await repo.get_by_filters(category_id=4, order="DESC")
  assert len(products) == 3
  assert products[0].id == 3
  assert products[2].id == 2

@pytest.mark.asyncio
async def test_get_by_filters_category_middle_category(db):
  await insert_categories_and_products(db)
  repo = ProductRepository(db)
  products = await repo.get_by_filters(category_id=3)
  assert len(products) == 5

@pytest.mark.asyncio
async def test_get_by_filters_category_exteral_category(db):
  await insert_categories_and_products(db)
  repo = ProductRepository(db)
  products = await repo.get_by_filters(category_id=1)
  assert len(products) == 8

@pytest.mark.asyncio
async def test_get_by_filters_category_all(db):
  await insert_categories_and_products(db)
  repo = ProductRepository(db)
  products = await repo.get_by_filters()
  assert len(products) == 8

@pytest.mark.asyncio
async def test_get_by_filters_category_mixed_parts(db):
  await insert_categories_and_products(db)
  repo = ProductRepository(db)
  products = await repo.get_by_filters(names=["bombus", "ener", "raw"])
  assert len(products) == 1
  product = products[0]
  assert product.id == 8

@pytest.mark.asyncio
async def test_get_by_id(db):
  product_id = await insert_line(db)
  repo = ProductRepository(db)
  product = await repo.get_by_id(product_id)
  assert product.name == "Karmel" and product.brand == "Auchan" and product.kcal == 300

@pytest.mark.asyncio
async def test_get_by_id_wrong_id(db):
  repo = ProductRepository(db)
  product = await repo.get_by_id(100)
  assert product is None


@pytest.mark.asyncio
async def test_insert_product(db):
  repo = ProductRepository(db)
  product = ProductCreate(name="Baton", brand="Auchan", kcal=300, reference_unit='g', category_id=None)

  await repo.insert(product)
  await repo.commit()

  cursor = await db.execute("""SELECT * FROM Product""")

  products = await cursor.fetchall()
  await cursor.close()

  assert len(products) == 1

  result_product = products[0]

  #print(ProductBase(**await repo.get_by_id(result_product['id'])))
  assert result_product["name"] == "Baton"
  assert result_product["brand"] == "Auchan"
  assert result_product["kcal"] == 300
  assert result_product["reference_amount"] == 100


@pytest.mark.asyncio
async def test_delete_product_by_id(db):
  product_id = await insert_line(db)
  repo = ProductRepository(db)
  await repo.delete(product_id)

  cursor = await db.execute(""" 
    SELECT * FROM Product
  """)
  products = await cursor.fetchall()
  await cursor.close()

  assert product_id is not None
  assert products == []

@pytest.mark.asyncio
async def test_delete_product_by_id_wrong_id(db):
  repo = ProductRepository(db)
  count = await repo.delete(100)
  assert count == 0

@pytest.mark.asyncio
async def test_update_product_by_id(db):
  product_id = await insert_line(db)
  repo = ProductRepository(db)
  product_update = ProductUpdate(name='bakłażan')
  
  await repo.update(product_id, product_update)
  await repo.commit()

  cursor = await db.execute(""" 
    SELECT name, brand, kcal FROM Product WHERE id  = ?
  """, (product_id,))

  products = await cursor.fetchall()
  await cursor.close()
  
  assert len(products) == 1
  product = products[0]
  assert product['name'] == 'bakłażan'
  assert product['brand'] == 'Auchan'
  assert product['kcal'] == 300


@pytest.mark.asyncio
async def test_update_product_by_id_empty_value(db):
  product_id = await insert_line(db)
  repo = ProductRepository(db)

  product_update = ProductTest()
  await repo.update(product_id, product_update)
  await repo.commit()

  cursor = await db.execute(""" 
    SELECT name, brand, kcal FROM Product WHERE id  = ?
  """, (product_id,))

  products = await cursor.fetchall()
  await cursor.close()
  
  assert len(products) == 1
  product = products[0]
  assert product['name'] == 'Karmel'
  assert product['brand'] == 'Auchan'
  assert product['kcal'] == 300

@pytest.mark.asyncio
async def test_update_product_tht_does_not_exist(db):
  repo = ProductRepository(db)
  product = ProductCreate(name="Baton", brand="Auchan", kcal=300, reference_unit='g', category_id=10)
  count = await repo.update(10, product)
  assert count == 0

@pytest.mark.asyncio
async def test_insert_product_category_does_not_exist(db):
  repo = ProductRepository(db)
  product = ProductCreate(name="Baton", brand="Auchan", kcal=300, reference_unit='g', category_id=10)
  with pytest.raises(ForeignKeyViolationError):
    await repo.insert(product)

@pytest.mark.asyncio
async def test_insert_product_with_existing_id(db):
  product_id = await insert_line(db)
  repo = ProductRepository(db)
  product = ProductTest(id=product_id, name="Baton", brand="Auchan", kcal=300, reference_unit='g', category_id=10)
  with pytest.raises(UniqueViolationError):
    await repo.insert(product)

@pytest.mark.asyncio
async def test_insert_empty_product(db):
  repo = ProductRepository(db)
  product = ProductTest()
  with pytest.raises(NotNullViolationError):
    await repo.insert(product)

@pytest.mark.asyncio
async def test_insert_product_with_string_kcal_type(db):
  repo = ProductRepository(db)
  product = ProductTestStrKcal(name="Baton", brand="Auchan", kcal="tak")
  with pytest.raises(TypeViolationError):
    await repo.insert(product)

@pytest.mark.asyncio
async def test_update_product_category_does_not_exist(db):
  repo = ProductRepository(db)
  product = ProductTest(id=1, name="Baton", brand="Auchan", kcal=300, reference_unit='g')
  product_id = await repo.insert(product)
  with pytest.raises(ForeignKeyViolationError):
    await repo.update(product_id, ProductTest(category_id=20))

@pytest.mark.asyncio
async def test_update_empty_product(db):
  repo = ProductRepository(db)
  product = ProductTest(id=1, name="Baton", brand="Auchan", kcal=300, reference_unit='g')
  product_id = await repo.insert(product)
  product_updated = await repo.update(product_id, ProductTest())
  assert  product_updated == 0

@pytest.mark.asyncio
async def test_update_product_with_string_kcal_type(db):
  repo = ProductRepository(db)
  product = ProductTest(id=1, name="Baton", brand="Auchan", kcal=300, reference_unit='g')
  product_id = await repo.insert(product)
  with pytest.raises(TypeViolationError):
    await repo.update(product_id, ProductTestStrKcal(kcal="tak"))