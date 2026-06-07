import pytest

from api.dependencies.filters import PaginationFilters, ProductsFilters
from api.services.product import ProductService
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
async def test_get_all_by_name_empty_string(fake_product_repository): #it's like none
  repo = fake_product_repository(
    [ProductTest(id=8, name="Raw Energy Baton kakaowy Bombus", brand="BB", kcal=300, category_id=10, name_search_standard="raw energy baton kakaowy bombus"),
     ProductTest(id=80, name="Raw Dzik", brand="BB", kcal=300, name_search_standard="raw dzik")
     ])
  product_filters = ProductsFilters(name='')
  pagination_filters = PaginationFilters()
  service = ProductService(repo)
  total, products = await service.get_all(product_filters=product_filters, pagination_filters=pagination_filters)
  assert len(products) == 2
  assert total == 2


@pytest.mark.asyncio
async def test_get_all_by_name_empty_spaces(fake_product_repository): #it's like none
  repo = fake_product_repository(
    [ProductTest(id=8, name="Raw Energy Baton kakaowy Bombus", brand="BB", kcal=300, category_id=10, name_search_standard="raw energy baton kakaowy bombus"),
     ProductTest(id=80, name="Raw Dzik", brand="BB", kcal=300, name_search_standard="raw dzik")
     ])
  product_filters = ProductsFilters(name=' ')
  pagination_filters = PaginationFilters()
  service = ProductService(repo)
  total, products = await service.get_all(product_filters=product_filters, pagination_filters=pagination_filters)
  assert len(products) == 2
  assert total == 2

@pytest.mark.asyncio
async def test_get_all_by_name_and_category(fake_product_repository): #it's like none
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