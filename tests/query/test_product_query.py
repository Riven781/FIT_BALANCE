import pytest
from product_catalog_context.infrastructure.aiosqlite_queries.product import ProductQueries
from product_catalog_context.domain.enums.product_searching import SortBy

async def insert_categories_and_products(db):
  cursor = await db.executescript("""
    INSERT INTO ProductCategory VALUES
      (1, "Produkty", NULL),
      (2, "Roślinne", 1),
      (3, "Zwierzęce", 1),
      (4, "Schab", 3),
      (5, "Boczek", 3);
                            
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


@pytest.mark.asyncio
async def test_get_by_filters_names(db):
  await insert_categories_and_products(db)
  query = ProductQueries(db)
  products = await query.get_detail_by_filters(names=['schab'])
  assert len(products) == 3



@pytest.mark.asyncio
async def test_get_by_filters_convert_polish_chars(db):
  await insert_categories_and_products(db)
  query = ProductQueries(db)
  products = await query.get_detail_by_filters(names=['cielecy'])
  assert len(products) == 1

@pytest.mark.asyncio
async def test_get_by_filters_parts_of_words(db):
  await insert_categories_and_products(db)
  query = ProductQueries(db)
  products = await query.get_detail_by_filters(names=['bo', 'kasz'])
  assert len(products) == 1

@pytest.mark.asyncio
async def test_get_by_filters_separted_parts_of_words(db):
  await insert_categories_and_products(db)
  query = ProductQueries(db)
  products = await query.get_detail_by_filters(names=['bo', 'gro'])
  assert len(products) == 0 #boczek and groszek must be in one product name (together)

@pytest.mark.asyncio
async def test_get_by_filters_separted_parts_of_words_with_categories(db):
  await insert_categories_and_products(db)
  query = ProductQueries(db)
  products = await query.get_detail_by_filters(names=['bo', 'gro'], category_id=5)
  assert len(products) == 0 #boczek and groszek must be in one product name (together)

@pytest.mark.asyncio
async def test_get_by_filters_part_of_words_in_middle(db):
  await insert_categories_and_products(db)
  query = ProductQueries(db)
  products = await query.get_detail_by_filters(names=['czek'])
  assert len(products) == 0


@pytest.mark.asyncio
async def test_get_by_filters_category_empty_db(db):
  query = ProductQueries(db)
  products = await query.get_detail_by_filters(category_id=10,sort_by=SortBy.KCAL, order="ASC")
  assert products == []


@pytest.mark.asyncio
async def test_get_by_filters_category_asc(db):
  await insert_categories_and_products(db)
  query = ProductQueries(db)
  products = await query.get_detail_by_filters(category_id=4)
  assert len(products) == 3
  assert products[0].product_id == 2
  assert products[2].product_id == 3

@pytest.mark.asyncio
async def test_get_by_filters_category_desc(db):
  await insert_categories_and_products(db)
  query = ProductQueries(db)
  products = await query.get_detail_by_filters(category_id=4, order="DESC")
  assert len(products) == 3
  assert products[0].product_id == 3
  assert products[2].product_id == 2

@pytest.mark.asyncio
async def test_get_by_filters_category_middle_category(db):
  await insert_categories_and_products(db)
  query = ProductQueries(db)
  products = await query.get_detail_by_filters(category_id=3)
  assert len(products) == 5

@pytest.mark.asyncio
async def test_get_by_filters_category_exteral_category(db):
  await insert_categories_and_products(db)
  query = ProductQueries(db)
  products = await query.get_detail_by_filters(category_id=1)
  assert len(products) == 8

@pytest.mark.asyncio
async def test_get_by_filters_category_all(db):
  await insert_categories_and_products(db)
  query = ProductQueries(db)
  products = await query.get_detail_by_filters()
  assert len(products) == 8

@pytest.mark.asyncio
async def test_get_by_filters_category_mixed_parts(db):
  await insert_categories_and_products(db)
  query = ProductQueries(db)
  products = await query.get_detail_by_filters(names=["bombus", "ener", "raw"])
  assert len(products) == 1
  product = products[0]
  assert product.product_id == 8

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
async def test_get_by_id(db):
  product_id = await insert_line(db)
  query = ProductQueries(db)
  product = await query.get_detail_by_id(product_id)
  assert product.name == "Karmel" and product.brand_name == "Auchan" and product.nutrition_facts.kcal == 300

@pytest.mark.asyncio
async def test_get_by_id_wrong_id(db):
  query = ProductQueries(db)
  product = await query.get_detail_by_id(100)
  assert product is None