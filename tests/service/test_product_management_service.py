import pytest
from product_catalog_context.domain.product.product import Product
from product_catalog_context.domain.product.nutrition_facts import NutritionFacts, Nutrients, ReferenceQuantity, Nutrients
from product_catalog_context.application.command.product import ProductCommand
from product_catalog_context.application.product_management_service import ProductManagementService
from product_catalog_context.application.errors.errors import ProductNotFoundError
from product_catalog_context.infrastructure.aiosqlite_repository.product_category_hierarchy import ProductCategoryHierarchyRepository
from product_catalog_context.domain.product.product_assignment import CategoryAssignment

#pytest tests/service/test_product_management_service.py

pytestmark = pytest.mark.usefixtures('insert_data')

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
async def test_create_one_product(product_management_service: ProductManagementService):
  product_command = ProductCommand(
    name="Raw Dzik", 
    brand_name="BB", 
    current_category_id=2, 
    nutrition_facts=
      NutritionFacts(
        reference_quantity=ReferenceQuantity(amount=100, unit='g'), 
        kcal=120, 
        nutrients=Nutrients()), 
    img_src=None)
  product_created = await product_management_service.create(product_command, 1)
  assert product_created.name_search_standard == 'raw dzik'
  assert product_created.name == 'Raw Dzik'

@pytest.mark.asyncio
async def test_create_empty_string_name(product_management_service: ProductManagementService):
  product_command = ProductCommand(
    name="", 
    brand_name="BB", 
    current_category_id=2, 
    nutrition_facts=
      NutritionFacts(
        reference_quantity=ReferenceQuantity(amount=100, unit='g'),
        kcal=120, 
        nutrients=Nutrients()), 
    img_src=None)
  with pytest.raises(ValueError):
    product_created = await product_management_service.create(product_command, 1)

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
async def test_update_wrong_id(product_management_service: ProductManagementService):
  new_info_about_product = ProductCommand(
    name="Żywiec zdrój", brand_name="BB", current_category_id=2,
    nutrition_facts=NutritionFacts(
    reference_quantity=ReferenceQuantity(amount=100, unit='g'),
    kcal=120, 
    nutrients=Nutrients()), img_src=None)
  
  with pytest.raises(ProductNotFoundError):
    await product_management_service.update(100, new_info_about_product, 1)


@pytest.mark.asyncio
async def test_update_one_product(product_management_service: ProductManagementService):
  nutrition_facts = NutritionFacts(reference_quantity=ReferenceQuantity(amount=100, unit='g'), kcal=300, nutrients=Nutrients())
  new_info_about_product = ProductCommand(name="Żywiec zdrój", brand_name="BB", current_category_id=5, nutrition_facts=nutrition_facts, img_src=None)
  await product_management_service.update(8, new_info_about_product, 1)
  product = await product_management_service.get(8)
  assert product.product_id == 8
  assert product.name == "Żywiec zdrój"
  assert product.name_search_standard == 'zywiec zdroj'
  assert product.brand_name == "BB"


@pytest.mark.asyncio
async def test_update_current_category_id(product_management_service: ProductManagementService):
  nutrition_facts = NutritionFacts(reference_quantity=ReferenceQuantity(amount=100, unit='g'), kcal=300, nutrients=Nutrients())
  new_info_about_product = ProductCommand(name="Raw Dzik", brand_name="BB", current_category_id=5, nutrition_facts=nutrition_facts, img_src=None)

  await product_management_service.update(8, new_info_about_product, 1)

  product = await product_management_service.get(8)
  assert product.product_id == 8
  assert product.name == "Raw Dzik"
  assert len(product.category_assignments) == 1
  
  assert 1 in product.category_assignments.keys()
  assert product.category_assignments[1].category_id == 5


@pytest.mark.asyncio
async def test_update_one_product_with_null_field(product_management_service: ProductManagementService):
  new_nutrition_facts = NutritionFacts(reference_quantity=ReferenceQuantity(amount=100, unit='g'), kcal=300, nutrients=Nutrients())
  new_info_about_product = ProductCommand(name="Raw Dzik", brand_name="BB", current_category_id=2, nutrition_facts=new_nutrition_facts, img_src=None)

  await product_management_service.update(8, new_info_about_product, 1)
  product = await product_management_service.get(8)
  assert product.product_id == 8
  assert product.name == "Raw Dzik"
  assert product.nutrition_facts.nutrients.fat == None
  assert product.brand_name == "BB"

@pytest.mark.asyncio
async def test_delete_one_product(product_management_service: ProductManagementService):
  await product_management_service.delete(8, 1)
  with pytest.raises(ProductNotFoundError):
    product = await product_management_service.get(8)

@pytest.mark.asyncio
async def test_delete_wrong_id(product_management_service: ProductManagementService):
  with pytest.raises(ProductNotFoundError):
    await product_management_service.delete(100, 1)
  