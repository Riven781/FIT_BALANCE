import pytest
from product_catalog_context.domain.product.product_repository import ProductRepository
from product_catalog_context.domain.product.nutrition_facts import Nutrients, NutritionFacts, ReferenceQuantity
from product_catalog_context.domain.product.product import Product
from product_catalog_context.domain.product.product_assignment import CategoryAssignment
from product_catalog_context.domain.repository.errors import CheckViolationError, ForeignKeyViolationError, NotNullViolationError, RepositoryError, RepositoryIntegrityError, RepositoryProgrammingError, RepositoryUnavailableError, TypeViolationError, UniqueViolationError, UnknownRepositoryError


pytestmark = pytest.mark.usefixtures("insert_data")

@pytest.mark.asyncio
async def test_get_by_id(product_repository: ProductRepository):
  product = await product_repository.get_by_id(1)
  assert product.product_id == 1
  assert product.name == 'Schab Drogi'
  assert product.nutrition_facts == NutritionFacts(kcal=300, reference_quantity=ReferenceQuantity(amount=100, unit='g'), nutrients=Nutrients(fat=100))
  assert product.name_search_standard == 'schab drogi'
  print(product.category_assignments)
  assert product.category_assignments == {1: CategoryAssignment(category_id=4, version=1), 2:CategoryAssignment(category_id=9, version=1)}


@pytest.mark.asyncio
async def test_get_by_id_not_existing_product(product_repository: ProductRepository):
  product = await product_repository.get_by_id(10)
  assert product is None

@pytest.mark.asyncio
async def test_delete(product_repository: ProductRepository, db_session):
  product = await product_repository.get_by_id(1)
  await product_repository.delete(product)
  await db_session.commit()
  product = await product_repository.get_by_id(1)
  assert product is None

@pytest.mark.asyncio
async def test_save_insert_new_product(product_repository: ProductRepository, db_session):
  new_product = Product(name='Jabłko', brand_name='Auchan', nutrition_facts=NutritionFacts(kcal=70, reference_quantity=ReferenceQuantity(amount=100, unit='g'), nutrients=Nutrients(fat=10)), name_search_standard='jablko', category_assignments={1:CategoryAssignment(category_id=2)})
  await product_repository.save(new_product)
  assert new_product.name == 'Jabłko'
  assert new_product.product_id is not None
  await db_session.commit()
  product = await product_repository.get_by_id(new_product.product_id)
  assert product.name == 'Jabłko'
  assert product.category_assignments == {1: CategoryAssignment(category_id=2, version=1)}

@pytest.mark.asyncio
async def test_save_insert_new_product_with_not_existing_category(product_repository: ProductRepository, db_session):
  new_product = Product(name='Jabłko', brand_name='Auchan', nutrition_facts=NutritionFacts(kcal=70, reference_quantity=ReferenceQuantity(amount=100, unit='g'), nutrients=Nutrients(fat=10)), name_search_standard='jablko', category_assignments={1:CategoryAssignment(category_id=200)})
  with pytest.raises(ForeignKeyViolationError):
    await product_repository.save(new_product)

@pytest.mark.asyncio
async def test_save_insert_new_product_with_not_existing_hierarchy(product_repository: ProductRepository, db_session):
  new_product = Product(name='Jabłko', brand_name='Auchan', nutrition_facts=NutritionFacts(kcal=70, reference_quantity=ReferenceQuantity(amount=100, unit='g'), nutrients=Nutrients(fat=10)), name_search_standard='jablko', category_assignments={199:CategoryAssignment(category_id=2)})
  with pytest.raises(ForeignKeyViolationError):
    await product_repository.save(new_product)

@pytest.mark.asyncio
async def test_save_update_product(product_repository: ProductRepository, db_session):
  product = await product_repository.get_by_id(1)
  product.assign_to_category(1, 2, product_editor_id=None, expected_version=1)
  product.rename('Schab Delux')
  await product_repository.save(product)
  assert product.name == 'Schab Delux'
  assert product.product_id == 1
  assert product.category_assignments == {1: CategoryAssignment(category_id=2, version=1), 2:CategoryAssignment(category_id=9, version=1)} #db doesnt do update version before commit
  await db_session.commit()
  product = await product_repository.get_by_id(1)
  assert product.name == 'Schab Delux'
  assert product.category_assignments == {1: CategoryAssignment(category_id=2, version=2), 2:CategoryAssignment(category_id=9, version=1)}

@pytest.mark.asyncio
async def test_get_total_without_planned_category(product_repository: ProductRepository):
  total = await product_repository.get_total_without_planned_category()
  assert total == 7

@pytest.mark.asyncio
async def test_get_without_planned_category_and_assignment_task(product_repository: ProductRepository):
  products = await product_repository.get_without_planned_category_and_assignment_task(category_id=4, hierarchy_id=2)
  assert len(products) == 2
  assert 2 in [product.product_id for product in products]
  assert 3 in [product.product_id for product in products]


@pytest.mark.asyncio
async def test_get_without_planned_category_and_assignment_task_with_limit(product_repository: ProductRepository):
  products = await product_repository.get_without_planned_category_and_assignment_task(category_id=4, hierarchy_id=2, limit=1)
  assert len(products) == 1
  assert 2 in [product.product_id for product in products]


@pytest.mark.asyncio
async def test_copy_category_assignments(product_repository: ProductRepository):
  await product_repository.copy_category_assignments(active_hierarchy_id=1, draft_hierarchy_id=3)
  product_1 = await product_repository.get_by_id(1)
  assert 3 in product_1.category_assignments and CategoryAssignment(category_id=14) in product_1.category_assignments.values()


@pytest.mark.asyncio
async def test_delete_category_assignments_by_category_id(product_repository: ProductRepository):
  await product_repository.delete_category_assignments_by_category_id(category_ids=[4, 5])
  product_1 = await product_repository.get_by_id(1)
  assert product_1.category_assignments == {2:CategoryAssignment(category_id=9, version=1)}
  product_2 = await product_repository.get_by_id(7)
  assert product_2.category_assignments == {}
  product_3 = await product_repository.get_by_id(8)
  assert product_3.category_assignments == {1:CategoryAssignment(category_id=2, version=1)}