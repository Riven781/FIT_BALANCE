import pytest
from product_catalog_context.domain.product.product import Product
from product_catalog_context.domain.product.nutrition_facts import NutritionFacts, Nutrients, ReferenceQuantity, Nutrients
from product_catalog_context.application.command.product import ProductCommand
from product_catalog_context.application.product_management_service import ProductManagementService
from product_catalog_context.application.errors.errors import ProductNotFoundError
from product_catalog_context.infrastructure.aiosqlite_repository.product_category_hierarchy import ProductCategoryHierarchyRepository

#pytest tests/service/test_product_management_service.py

async def insert_users(db):
  async with db.executescript(
    """
    INSERT INTO User(id, username, email, hashed_password) VALUES 
      (1, 'ZYZ','xyz@gm.c','xyz'), 
      (2, 'ABC','abc@gm.c','abc');
    
    INSERT INTO UserRoles(user_id, version) VALUES 
      (1, 1), 
      (2, 1);
    
    INSERT INTO UserRole(user_id, role) VALUES 
      (1, 'product_editor'),
      (2, 'catalog_manager');
    """
  ) as cursor:
    pass  

@pytest.mark.asyncio
async def test_create_one_product(db, product_repository, hierarchy_repository, access_adapter):
  await insert_users(db)
  service = ProductManagementService(product_repository, hierarchy_repository, access_adapter)
  product_command = ProductCommand(
    name="Raw Dzik", 
    brand_name="BB", 
    current_category_id=10, 
    nutrition_facts=
      NutritionFacts(
        reference_quantity=ReferenceQuantity(amount=100, unit='g'), 
        kcal=120, 
        nutrients=Nutrients()), 
    img_src=None)
  product_created = await service.create(product_command, 1)
  print(product_created.name)
  assert product_created.name_search_standard == 'raw dzik'
  assert product_created.name == 'Raw Dzik'

@pytest.mark.asyncio
async def test_create_empty_string_name(db, product_repository, hierarchy_repository, access_adapter):
  await insert_users(db)
  service = ProductManagementService(product_repository, hierarchy_repository, access_adapter)
  product_command = ProductCommand(
    name="", 
    brand_name="BB", 
    current_category_id=10, 
    nutrition_facts=
      NutritionFacts(
        reference_quantity=ReferenceQuantity(amount=100, unit='g'),
        kcal=120, 
        nutrients=Nutrients()), 
    img_src=None)
  with pytest.raises(ValueError):
    product_created = await service.create(product_command, 1)

async def insert_product(db):
  async with db.executescript(
    """
    INSERT INTO Product(id, name, brand_name, kcal, reference_amount, reference_unit, name_search_standard, fat) VALUES 
      (80, 'Raw Dzik','BB', 120, 100, 'g', 'raw dzik', 100);

    INSERT INTO ProductCategoryAssignment(product_id, node_id) VALUES
      (80, 10);
    """
    ) as cursor:
        pass  


@pytest.mark.asyncio #with error (i need to create better exception hierarchy)
async def test_update_wrong_id(db, product_repository, hierarchy_repository, access_adapter):
  await insert_users(db)
  await insert_product(db)
  new_info_about_product = ProductCommand(
    name="Żywiec zdrój", brand_name="BB", current_category_id=10,
    nutrition_facts=NutritionFacts(
    reference_quantity=ReferenceQuantity(amount=100, unit='g'),
    kcal=120, 
    nutrients=Nutrients()), img_src=None)
  service = ProductManagementService(product_repository, hierarchy_repository, access_adapter)
  
  with pytest.raises(ProductNotFoundError):
    await service.update(100, new_info_about_product, 1)

  product = await service.get(80)
  assert product.product_id == 80
  assert product.name == "Raw Dzik"

@pytest.mark.asyncio
async def test_update_one_product(db, product_repository, hierarchy_repository, access_adapter):
  nutrition_facts = NutritionFacts(reference_quantity=ReferenceQuantity(amount=100, unit='g'), kcal=300, nutrients=Nutrients())
  await insert_users(db)
  await insert_product(db)
  new_info_about_product = ProductCommand(name="Żywiec zdrój", brand_name="BB", current_category_id=10, nutrition_facts=nutrition_facts, img_src=None)
  service = ProductManagementService(product_repository, hierarchy_repository, access_adapter)

  await service.update(80, new_info_about_product, 1)

  product = await service.get(80)
  assert product.product_id == 80
  assert product.name == "Żywiec zdrój"
  assert product.name_search_standard == 'zywiec zdroj'
  assert product.brand_name == "BB"


@pytest.mark.asyncio
async def test_update_current_category_id(db, product_repository, hierarchy_repository, access_adapter):
  await insert_users(db)
  await insert_product(db)
  nutrition_facts = NutritionFacts(reference_quantity=ReferenceQuantity(amount=100, unit='g'), kcal=300, nutrients=Nutrients())
  new_info_about_product = ProductCommand(name="Raw Dzik", brand_name="BB", current_category_id=11, nutrition_facts=nutrition_facts, img_src=None)
  service = ProductManagementService(product_repository, hierarchy_repository, access_adapter)

  await service.update(80, new_info_about_product, 1)

  product = await service.get(80)
  assert product.product_id == 80
  assert product.name == "Raw Dzik"
  assert len(product.category_assignments) == 1
  assert product.category_assignments == {1:11}

@pytest.mark.asyncio
async def test_update_one_product_with_null_field(db, product_repository, hierarchy_repository, access_adapter):
  await insert_users(db)
  await insert_product(db)
  new_nutrition_facts = NutritionFacts(reference_quantity=ReferenceQuantity(amount=100, unit='g'), kcal=300, nutrients=Nutrients())
  new_info_about_product = ProductCommand(name="Raw Dzik", brand_name="BB", current_category_id=10, nutrition_facts=new_nutrition_facts, img_src=None)

  service = ProductManagementService(product_repository, hierarchy_repository, access_adapter)
  await service.update(80, new_info_about_product, 1)
  product = await service.get(80)
  assert product.product_id == 80
  assert product.name == "Raw Dzik"
  assert product.nutrition_facts.nutrients.fat == None
  assert product.brand_name == "BB"

@pytest.mark.asyncio
async def test_delete_one_product(db, product_repository, hierarchy_repository, access_adapter):
  await insert_users(db)
  await insert_product(db)
  service = ProductManagementService(product_repository, hierarchy_repository, access_adapter)
  await service.delete(80, 1)
  with pytest.raises(ProductNotFoundError):
    product = await service.get(80)

@pytest.mark.asyncio
async def test_delete_wrong_id(db, product_repository, hierarchy_repository, access_adapter):
  await insert_users(db)
  service = ProductManagementService(product_repository, hierarchy_repository, access_adapter)
  with pytest.raises(ProductNotFoundError):
    await service.delete(100, 1)
  