import pytest
from product_catalog_context.domain.product import Product
from product_catalog_context.domain.nutrition_facts import NutritionFacts, Nutrients, ReferenceQuantity
from product_catalog_context.application.command.product import ProductCommand
from product_catalog_context.application.product_management_service import ProductManagementService
from product_catalog_context.application.errors.errors import ProductNotFoundError

#pytest tests/service/test_product_management_service.py

@pytest.mark.asyncio
async def test_create_one_product(fake_product_repository):
  repo = fake_product_repository(
    [])
  service = ProductManagementService(repo)
  product_command = ProductCommand(name="Raw Dzik", brand_name="BB", current_category_id=10, nutrition_facts=None, img_src=None)
  product_created = await service.create(product_command)
  print(product_created.name)
  assert product_created.name_search_standard == 'raw dzik'
  assert product_created.name == 'Raw Dzik'

@pytest.mark.asyncio
async def test_create_empty_string_name(fake_product_repository):
  repo = fake_product_repository(
    [])
  service = ProductManagementService(repo)
  product_command = ProductCommand(name="", brand_name="BB", current_category_id=10, nutrition_facts=None, img_src=None)
  with pytest.raises(ValueError):
    product_created = await service.create(product_command)


@pytest.mark.asyncio #with error (i need to create better exception hierarchy)
async def test_update_wrong_id(fake_product_repository):
  repo = fake_product_repository(
    [Product(product_id=80, name="Raw Dzik", brand_name="BB", nutrition_facts=None, current_category_id=10, name_search_standard='raw dzik')])
  new_info_about_product = ProductCommand(name="Żywiec zdrój", brand_name="BB", current_category_id=10, nutrition_facts=None, img_src=None)
  service = ProductManagementService(repo)
  
  with pytest.raises(ProductNotFoundError):
    await service.update(100, new_info_about_product)

  product = await service.get(80)
  assert product.product_id == 80
  assert product.name == "Raw Dzik"

@pytest.mark.asyncio
async def test_update_one_product(fake_product_repository):
  nutrition_facts = NutritionFacts(reference_quantity=ReferenceQuantity(amount=100, unit='g'), kcal=300, nutrients=Nutrients())
  repo = fake_product_repository(
    [Product(
      product_id=80, 
      name="Raw Dzik", 
      brand_name="BB", 
      nutrition_facts=nutrition_facts, 
      current_category_id=10, 
      name_search_standard='raw dzik')])
  new_info_about_product = ProductCommand(name="Żywiec zdrój", brand_name="BB", current_category_id=10, nutrition_facts=nutrition_facts, img_src=None)
  service = ProductManagementService(repo)

  await service.update(80, new_info_about_product)

  product = await service.get(80)
  assert product.product_id == 80
  assert product.name == "Żywiec zdrój"
  assert product.name_search_standard == 'zywiec zdroj'
  assert product.brand_name == "BB"

@pytest.mark.asyncio
async def test_update_one_product_with_null_field(fake_product_repository):
  nutrition_facts = NutritionFacts(reference_quantity=ReferenceQuantity(amount=100, unit='g'), kcal=300, nutrients=Nutrients(fat=100))
  repo = fake_product_repository(
    [Product(
      product_id=80, 
      name="Raw Dzik", 
      brand_name="BB", 
      nutrition_facts=nutrition_facts, 
      current_category_id=10, 
      name_search_standard='raw dzik')])
  new_nutrition_facts = NutritionFacts(reference_quantity=ReferenceQuantity(amount=100, unit='g'), kcal=300, nutrients=Nutrients())
  new_info_about_product = ProductCommand(name="Raw Dzik", brand_name="BB", current_category_id=10, nutrition_facts=new_nutrition_facts, img_src=None)

  service = ProductManagementService(repo)
  await service.update(80, new_info_about_product)
  product = await service.get(80)
  assert product.product_id == 80
  assert product.name == "Raw Dzik"
  assert product.nutrition_facts.nutrients.fat == None
  assert product.brand_name == "BB"

@pytest.mark.asyncio
async def test_delete_one_product(fake_product_repository):
  repo = fake_product_repository(
    [Product(product_id=80, name="Raw Dzik", brand_name="BB", nutrition_facts=None, current_category_id=10, name_search_standard='raw dzik')])
  service = ProductManagementService(repo)
  await service.delete(80)
  with pytest.raises(ProductNotFoundError):
    product = await service.get(80)

@pytest.mark.asyncio
async def test_delete_wrong_id(fake_product_repository):
  repo = fake_product_repository(
    [Product(product_id=80, name="Raw Dzik", brand_name="BB", nutrition_facts=None, current_category_id=10, name_search_standard='raw dzik')])
  service = ProductManagementService(repo)
  with pytest.raises(ProductNotFoundError):
    await service.delete(100)
  