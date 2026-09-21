import pytest
import pytest_asyncio
import asyncio
from product_catalog_context.application.product_management_service import ProductManagementService
from product_catalog_context.application.command.product import ProductCommand
from product_catalog_context.domain.product.nutrition_facts import NutritionFacts, Nutrients, ReferenceQuantity, Nutrients
from product_catalog_context.infrastructure.sql_alchemy_repository.product_issue import SqlAlchemyProductIssueRepository
from product_catalog_context.domain.issues.product_issue_status import ProductIssueStatus
from product_catalog_context.domain.tasks.category_assignment_task_repository import CategoryAssignmentTaskRepository
from product_catalog_context.domain.tasks.category_assignment_task_status import CategoryAssignmentTaskStatus

from product_catalog_context.application.product_issue_service import ProductIssueService
from product_catalog_context.domain.product.product_repository import ProductRepository
from product_catalog_context.infrastructure.outbox.repository import OutboxDAO
from product_catalog_context.domain.product.product_assignment import CategoryAssignment
from product_catalog_context.infrastructure.sql_alchemy_repository.unit_of_work import SqlAlchemyUnitOfWork

pytestmark = pytest.mark.usefixtures('insert_data', 'outbox_dispatcher')


@pytest.mark.asyncio
async def test_update_product_data_mark_as_obsolete_only_pending_issues(
  product_management_service: ProductManagementService,
  product_issue_repository: SqlAlchemyProductIssueRepository
):
  nutrition_facts = NutritionFacts(reference_quantity=ReferenceQuantity(amount=100, unit='g'), kcal=210, nutrients=Nutrients(fat=200))
  new_info_about_product = ProductCommand(name="Schab Drogi", brand_name="Auchan", current_category_id=4, planned_category_id=9, nutrition_facts=nutrition_facts, img_src=None)
  await product_management_service.update(product_id=1, product_command=new_info_about_product, product_editor_id=10)
  await asyncio.sleep(1)
  product = await product_management_service.get(1)
  assert product.kcal == 210
  issue_kcal = await product_issue_repository.get_by_id(1)
  assert issue_kcal.status == ProductIssueStatus.OBSOLETE
  issue_fat = await product_issue_repository.get_by_id(2)
  assert issue_fat.status == ProductIssueStatus.CONFIRMED

@pytest.mark.asyncio
async def test_update_product_data_2_pending_issue(
  product_management_service: ProductManagementService,
  product_issue_repository: SqlAlchemyProductIssueRepository
):
  nutrition_facts = NutritionFacts(reference_quantity=ReferenceQuantity(amount=100, unit='g'), kcal=210, nutrients=Nutrients(fat=200, sugars=10))
  new_info_about_product = ProductCommand(name="Schab Drogi", brand_name="Auchan", current_category_id=4, planned_category_id=9, nutrition_facts=nutrition_facts, img_src=None)
  await product_management_service.update(product_id=1, product_command=new_info_about_product, product_editor_id=10)
  await asyncio.sleep(1)
  product = await product_management_service.get(1)
  assert product.kcal == 210
  issue_kcal = await product_issue_repository.get_by_id(1)
  assert issue_kcal.status == ProductIssueStatus.OBSOLETE
  issue_sugars = await product_issue_repository.get_by_id(3)
  assert issue_sugars.status == ProductIssueStatus.OBSOLETE
  issue_fat = await product_issue_repository.get_by_id(2)
  assert issue_fat.status == ProductIssueStatus.CONFIRMED

@pytest.mark.asyncio
async def test_update_planned_category_two_times_in_the_same_time(
  fake_access_adapter, message_publisher, session_factory,
):
  nutrition_facts = NutritionFacts(reference_quantity=ReferenceQuantity(amount=100, unit='g'), kcal=250, nutrients=Nutrients(fat=120))

  service1 = ProductManagementService(SqlAlchemyUnitOfWork(session_factory), fake_access_adapter, message_publisher)
  service2 = ProductManagementService(SqlAlchemyUnitOfWork(session_factory), fake_access_adapter, message_publisher)
  #nadpisywanie!!!
  await asyncio.gather(
    service1.update(2, ProductCommand(name="Schab Tani", brand_name="Rambert", current_category_id=4, planned_category_id=9, nutrition_facts=nutrition_facts, img_src=None), product_editor_id=10), 
    service2.update(2, ProductCommand(name="Schab Tani", brand_name="Rambert", current_category_id=4, planned_category_id=8, nutrition_facts=nutrition_facts, img_src=None), product_editor_id=10))
  product = await service1.get(2)
  await asyncio.sleep(1)

  assert product.category_assignments.get(2) == CategoryAssignment(category_id=9, assigned_by=10)

@pytest.mark.asyncio
async def test_update_planned_category_cancel_task(
  product_management_service: ProductManagementService,
  category_assignment_task_repository: CategoryAssignmentTaskRepository
):
  nutrition_facts = NutritionFacts(reference_quantity=ReferenceQuantity(amount=100, unit='g'), kcal=110, nutrients=Nutrients(fat=100))
  new_product_info = ProductCommand(name="Schab Tani", brand_name="Rambert", current_category_id=4, planned_category_id=10, nutrition_facts=nutrition_facts, img_src=None)

 
  await product_management_service.update(2, new_product_info, product_editor_id=10)

  product = await product_management_service.get(2)
  assert product.category_assignments.get(2) == CategoryAssignment(category_id=10, assigned_by=10)
  assert product.nutrition_facts.kcal == 110
  assert product.nutrition_facts.nutrients.fat == 100
  await asyncio.sleep(1)

  task = await category_assignment_task_repository.get_by_product_and_hierarchy(2, 2)
  assert task.status == CategoryAssignmentTaskStatus.CANCELLED


@pytest.mark.asyncio
async def test_update_planned_category_complete_task(
  product_management_service: ProductManagementService,
  category_assignment_task_repository: CategoryAssignmentTaskRepository
):
  nutrition_facts = NutritionFacts(reference_quantity=ReferenceQuantity(amount=100, unit='g'), kcal=110, nutrients=Nutrients(fat=100))
  new_product_info = ProductCommand(name="Schab Tani", brand_name="Rambert", current_category_id=4, planned_category_id=10, nutrition_facts=nutrition_facts, img_src=None)

 
  await product_management_service.update(2, new_product_info, product_editor_id=1)

  product = await product_management_service.get(2)
  assert product.category_assignments.get(2) == CategoryAssignment(category_id=10, assigned_by=1)
  assert product.nutrition_facts.kcal == 110
  assert product.nutrition_facts.nutrients.fat == 100
  await asyncio.sleep(1)

  task = await category_assignment_task_repository.get_by_product_and_hierarchy(2, 2)
  assert task.status == CategoryAssignmentTaskStatus.COMPLETED
