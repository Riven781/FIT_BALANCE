import pytest
from product_catalog_context.domain.product.product import Product
from product_catalog_context.domain.product.nutrition_facts import NutritionFacts, Nutrients, ReferenceQuantity
from product_catalog_context.application.command.product import ProductCommand, ProductsFiltersCommand, PaginationFiltersCommand
from product_catalog_context.application.product_management_service import ProductManagementService
from product_catalog_context.application.errors.errors import ProductNotFoundError
from product_catalog_context.application.product_query_service import ProductQueryService
@pytest.mark.asyncio
async def test_get_correct_id(fake_product_queries):
  queries = fake_product_queries([Product(product_id=8, name="Raw Energy Baton kakaowy Bombus", brand_name="BB", nutrition_facts=None, category_assignments={1:10})])
  service = ProductQueryService(queries)
  product = await service.get(8)
  assert product.product_id == 8

@pytest.mark.asyncio
async def test_get_wrong_id(fake_product_queries):
  queries = fake_product_queries([Product(product_id=8, name="Raw Energy Baton kakaowy Bombus", brand_name="BB", nutrition_facts=None, category_assignments={1:10})])
  service = ProductQueryService(queries)
  with pytest.raises(ProductNotFoundError):
    product = await service.get(10)

@pytest.mark.asyncio
async def test_get_all_without_arguments(fake_product_queries):
  queries = fake_product_queries(
    [Product(product_id=8, name="Raw Energy Baton kakaowy Bombus", brand_name="BB", nutrition_facts=None, category_assignments={1:10}),
     Product(product_id=80, name="Raw Dzik", brand_name="BB", nutrition_facts=None, category_assignments={1:10})
     ])
  product_filters = ProductsFiltersCommand(name=None)
  pagination_filters = PaginationFiltersCommand(page=1, limit=20)
  service = ProductQueryService(queries)
  products = await service.get_all(product_filters=product_filters, pagination_filters=pagination_filters)
  assert len(products) == 2

@pytest.mark.asyncio
async def test_get_all_by_category_correct_category_id(fake_product_queries):
  queries = fake_product_queries(
    [Product(product_id=8, name="Raw Energy Baton kakaowy Bombus", brand_name="BB", nutrition_facts=None, category_assignments={1:10}),
     Product(product_id=80, name="Raw Dzik", brand_name="BB", nutrition_facts=None, category_assignments={1:20})
    ])
  product_filters = ProductsFiltersCommand(name=None, category_id=10)
  pagination_filters = PaginationFiltersCommand(page=1, limit=20)
  service = ProductQueryService(queries)
  total, products = await service.get_all(product_filters=product_filters, pagination_filters=pagination_filters)
  assert len(products) == 1
  assert total == 1
  assert products[0].product_id == 8

@pytest.mark.asyncio
async def test_get_all_by_category_wrong_category_id(fake_product_queries):
  queries = fake_product_queries(
    [Product(product_id=8, name="Raw Energy Baton kakaowy Bombus", brand_name="BB", nutrition_facts=None, category_assignments={1:10}),
     Product(product_id=80, name="Raw Dzik", brand_name="BB", nutrition_facts=None, category_assignments={1:20})
    ])
  product_filters = ProductsFiltersCommand(name=None, category_id=50)
  pagination_filters = PaginationFiltersCommand(page=1, limit=20)
  service = ProductQueryService(queries)
  total, products = await service.get_all(product_filters=product_filters, pagination_filters=pagination_filters)
  assert len(products) == 0
  assert total == 0

@pytest.mark.asyncio
async def test_get_all_by_name_correct_name(fake_product_queries):
  queries = fake_product_queries(
    [Product(product_id=8, name="Raw Energy Baton kakaowy Bombus", brand_name="BB", nutrition_facts=None, category_assignments={1:10}),
     Product(product_id=80, name="Raw Dzik", brand_name="BB", nutrition_facts=None, category_assignments={1:10})
    ])
  product_filters = ProductsFiltersCommand(name='baton')
  pagination_filters = PaginationFiltersCommand(page=1, limit=20)
  service = ProductQueryService(queries)
  total, products = await service.get_all(product_filters=product_filters, pagination_filters=pagination_filters)
  assert len(products) == 1
  assert total == 1
  assert products[0].product_id == 8

@pytest.mark.asyncio
async def test_get_all_by_name_correct_name_two_words(fake_product_queries):
  queries = fake_product_queries(
     [Product(product_id=8, name="Raw Energy Baton kakaowy Bombus", brand_name="BB", nutrition_facts=None, category_assignments={1:10}),
      Product(product_id=80, name="Raw Dzik", brand_name="BB", nutrition_facts=None, category_assignments={1:20})
     ])
  product_filters = ProductsFiltersCommand(name='baton bom')
  pagination_filters = PaginationFiltersCommand(page=1, limit=20)
  service = ProductQueryService(queries)
  total, products = await service.get_all(product_filters=product_filters, pagination_filters=pagination_filters)
  assert len(products) == 1
  assert total == 1
  assert products[0].product_id == 8


@pytest.mark.asyncio
async def test_get_all_by_name_empty_string(fake_product_queries):
  queries = fake_product_queries(
     [Product(product_id=8, name="Raw Energy Baton kakaowy Bombus", brand_name="BB", nutrition_facts=None, category_assignments={1:10}),
      Product(product_id=80, name="Raw Dzik", brand_name="BB", nutrition_facts=None, category_assignments={1:20})
     ])
  product_filters = ProductsFiltersCommand(name='')
  pagination_filters = PaginationFiltersCommand(page=1, limit=20)
  service = ProductQueryService(queries)
  total, products = await service.get_all(product_filters=product_filters, pagination_filters=pagination_filters)
  assert len(products) == 0
  assert total == 0


@pytest.mark.asyncio
async def test_get_all_by_name_empty_spaces(fake_product_queries):
  queries = fake_product_queries(
     [Product(product_id=8, name="Raw Energy Baton kakaowy Bombus", brand_name="BB", nutrition_facts=None, category_assignments={1:10}, name_search_standard="raw energy baton kakaowy bombus"),
      Product(product_id=80, name="Raw Dzik", brand_name="BB", nutrition_facts=None, category_assignments={1:20}, name_search_standard="raw dzik")
     ])
  product_filters = ProductsFiltersCommand(name=' ')
  pagination_filters = PaginationFiltersCommand(page=1, limit=20)
  service = ProductQueryService(queries)
  total, products = await service.get_all(product_filters=product_filters, pagination_filters=pagination_filters)
  assert len(products) == 0
  assert total == 0


@pytest.mark.asyncio
async def test_get_all_by_name_and_category(fake_product_queries): 
  queries = fake_product_queries(
     [Product(product_id=8, name="Raw Energy Baton kakaowy Bombus", brand_name="BB", nutrition_facts=None, category_assignments={1:10}, name_search_standard="raw energy baton kakaowy bombus"),
      Product(product_id=80, name="Raw Dzik", brand_name="BB", nutrition_facts=None, category_assignments={1:20}, name_search_standard="raw dzik")
     ])
  product_filters = ProductsFiltersCommand(name='baton', category_id=10)
  pagination_filters = PaginationFiltersCommand(page=1, limit=20)
  service = ProductQueryService(queries)
  total, products = await service.get_all(product_filters=product_filters, pagination_filters=pagination_filters)
  assert len(products) == 1
  assert total == 1
  assert products[0].product_id == 8