import pytest

from api.dependencies.filters import PaginationFilters, ProductsFilters
from api.services.product import ProductService
from httpx import delete
from tests.schema import ProductTest

@pytest.mark.asyncio
async def test_get_correct_id(fake_product_repository):
  repo = fake_product_repository([ProductTest(id=8, name="Raw Energy Baton kakaowy Bombus", brand="BB", kcal=300)])
  service = ProductService(repo)
  product = await service.get(8)
  assert product.id == 8


@pytest.mark.asyncio
async def test_get_wrong_id(fake_product_repository):
  repo = fake_product_repository([ProductTest(id=8, name="Raw Energy Baton kakaowy Bombus", brand="BB", kcal=300)])
  service = ProductService(repo)
  product = await service.get(10)
  assert product is None

@pytest.mark.asyncio
async def test_get_all_without_arguments(fake_product_repository):
  repo = fake_product_repository(
    [ProductTest(id=8, name="Raw Energy Baton kakaowy Bombus", brand="BB", kcal=300),
     ProductTest(id=80, name="Raw Dzik", brand="BB", kcal=300)
     ])
  product_filters = ProductsFilters(name=None)
  pagination_filters = PaginationFilters()
  service = ProductService(repo)
  products = await service.get_all(product_filters=product_filters, pagination_filters=pagination_filters)
  assert len(products) == 2

@pytest.mark.asyncio
async def test_get_all_by_category_correct_category_id(fake_product_repository):
  repo = fake_product_repository(
    [ProductTest(id=8, name="Raw Energy Baton kakaowy Bombus", brand="BB", kcal=300, category_id=10),
     ProductTest(id=80, name="Raw Dzik", brand="BB", kcal=300)
     ])
  product_filters = ProductsFilters(name=None, category_id=10)
  pagination_filters = PaginationFilters()
  service = ProductService(repo)
  total, products = await service.get_all(product_filters=product_filters, pagination_filters=pagination_filters)
  assert len(products) == 1
  assert total == 1
  assert products[0].id == 8
  

@pytest.mark.asyncio
async def test_get_all_by_category_wrong_category_id(fake_product_repository):
  repo = fake_product_repository(
    [ProductTest(id=8, name="Raw Energy Baton kakaowy Bombus", brand="BB", kcal=300, category_id=10),
     ProductTest(id=80, name="Raw Dzik", brand="BB", kcal=300)
     ])
  product_filters = ProductsFilters(name=None, category_id=50)
  pagination_filters = PaginationFilters()
  service = ProductService(repo)
  total, products = await service.get_all(product_filters=product_filters, pagination_filters=pagination_filters)
  assert len(products) == 0
  assert total == 0

@pytest.mark.asyncio
async def test_get_all_by_name_correct_name(fake_product_repository):
  repo = fake_product_repository(
    [ProductTest(id=8, name="Raw Energy Baton kakaowy Bombus", brand="BB", kcal=300, category_id=10, name_search_standard="raw energy baton kakaowy bombus"),
     ProductTest(id=80, name="Raw Dzik", brand="BB", kcal=300, name_search_standard="raw dzik")
     ])
  product_filters = ProductsFilters(name='baton')
  pagination_filters = PaginationFilters()
  service = ProductService(repo)
  total, products = await service.get_all(product_filters=product_filters, pagination_filters=pagination_filters)
  assert len(products) == 1
  assert total == 1
  assert products[0].id == 8

@pytest.mark.asyncio
async def test_get_all_by_name_correct_name_two_words(fake_product_repository):
  repo = fake_product_repository(
    [ProductTest(id=8, name="Raw Energy Baton kakaowy Bombus", brand="BB", kcal=300, category_id=10, name_search_standard="raw energy baton kakaowy bombus"),
     ProductTest(id=80, name="Raw Dzik", brand="BB", kcal=300, name_search_standard="raw dzik")
     ])
  product_filters = ProductsFilters(name='baton bom')
  pagination_filters = PaginationFilters()
  service = ProductService(repo)
  total, products = await service.get_all(product_filters=product_filters, pagination_filters=pagination_filters)
  assert len(products) == 1
  assert total == 1
  assert products[0].id == 8

@pytest.mark.asyncio
async def test_get_all_by_name_empty_string(fake_product_repository):
  repo = fake_product_repository(
    [ProductTest(id=8, name="Raw Energy Baton kakaowy Bombus", brand="BB", kcal=300, category_id=10, name_search_standard="raw energy baton kakaowy bombus"),
     ProductTest(id=80, name="Raw Dzik", brand="BB", kcal=300, name_search_standard="raw dzik")
     ])
  product_filters = ProductsFilters(name='')
  pagination_filters = PaginationFilters()
  service = ProductService(repo)
  total, products = await service.get_all(product_filters=product_filters, pagination_filters=pagination_filters)
  assert len(products) == 0
  assert total == 0


@pytest.mark.asyncio
async def test_get_all_by_name_empty_spaces(fake_product_repository):
  repo = fake_product_repository(
    [ProductTest(id=8, name="Raw Energy Baton kakaowy Bombus", brand="BB", kcal=300, category_id=10, name_search_standard="raw energy baton kakaowy bombus"),
     ProductTest(id=80, name="Raw Dzik", brand="BB", kcal=300, name_search_standard="raw dzik")
     ])
  product_filters = ProductsFilters(name=' ')
  pagination_filters = PaginationFilters()
  service = ProductService(repo)
  total, products = await service.get_all(product_filters=product_filters, pagination_filters=pagination_filters)
  assert len(products) == 0
  assert total == 0

@pytest.mark.asyncio
async def test_get_all_by_name_and_category(fake_product_repository): 
  repo = fake_product_repository(
    [ProductTest(id=8, name="Raw Energy Baton kakaowy Bombus", brand="BB", kcal=300, category_id=10, name_search_standard="raw energy baton kakaowy bombus"),
     ProductTest(id=80, name="Raw Dzik", brand="BB", kcal=300, name_search_standard="raw dzik", category_id=10)
     ])
  product_filters = ProductsFilters(name='baton', )
  pagination_filters = PaginationFilters()
  service = ProductService(repo)
  total, products = await service.get_all(product_filters=product_filters, pagination_filters=pagination_filters)
  assert len(products) == 1
  assert total == 1
  assert products[0].id == 8


@pytest.mark.asyncio
async def test_create_one_product(fake_product_repository):
  repo = fake_product_repository(
    [])
  product = ProductTest(id=80, name="Raw Dzik", brand="BB", kcal=300, category_id=10)
  service = ProductService(repo)
  product_created = await service.create(product)
  assert product_created.id == 80
  assert product_created.name_search_standard == 'raw dzik'


@pytest.mark.asyncio
async def test_create_empty_string_name(fake_product_repository):
  repo = fake_product_repository(
    [])
  product = ProductTest(id=80, name="", brand="BB", kcal=300, category_id=10)
  service = ProductService(repo)
  product_created = await service.create(product)
  assert product_created.id == 80
  assert product_created.name_search_standard == ''

@pytest.mark.asyncio
async def test_update_one_product(fake_product_repository):
  repo = fake_product_repository(
    [ProductTest(id=80, name="Raw Dzik", brand="BB", kcal=300, category_id=10, name_search_standard='raw dzik')])
  new_info_about_product = ProductTest(name="Żywiec zdrój")
  service = ProductService(repo)
  await service.update(80, new_info_about_product)
  product = await service.get(80)
  assert product.id == 80
  assert product.name == "Żywiec zdrój"
  assert product.name_search_standard == 'zywiec zdroj'
  assert product.brand == "BB"


@pytest.mark.asyncio #with error (i need to create better exception hierarchy)
@pytest.mark.xfail
async def test_update_wrong_id(fake_product_repository):
  repo = fake_product_repository(
    [ProductTest(id=80, name="Raw Dzik", brand="BB", kcal=300, category_id=10, name_search_standard='raw dzik')])
  new_info_about_product = ProductTest(name="Żywiec zdrój")
  service = ProductService(repo)
  await service.update(100, new_info_about_product)
  product = await service.get(80)
  assert product.id == 80
  assert product.name == "Raw Dzik"
  

@pytest.mark.asyncio
async def test_delete_one_product(fake_product_repository):
  repo = fake_product_repository(
    [ProductTest(id=80, name="Raw Dzik", brand="BB", kcal=300, category_id=10, name_search_standard='raw dzik')])
  service = ProductService(repo)
  await service.delete(80)
  product = await service.get(80)
  assert product == None


@pytest.mark.asyncio
@pytest.mark.xfail
async def test_delete_wrong_id(fake_product_repository):
  repo = fake_product_repository(
    [ProductTest(id=80, name="Raw Dzik", brand="BB", kcal=300, category_id=10, name_search_standard='raw dzik')])
  service = ProductService(repo)
  await service.delete(100)
  product = await service.get(80)
  assert product.id== 80