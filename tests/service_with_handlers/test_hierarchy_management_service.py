import pytest
from product_catalog_context.application.category_hierarchy_management_service import CategoryHierarchyManagementService
from product_catalog_context.domain.category_hierarchy.product_category_hierarchy_status import ProductCategoryHierarchyStatus
from product_catalog_context.domain.tasks.category_assignment_task_repository import CategoryAssignmentTaskRepository
from product_catalog_context.application.product_management_service import ProductManagementService
from product_catalog_context.domain.product.nutrition_facts import NutritionFacts, Nutrients, ReferenceQuantity, Nutrients
from product_catalog_context.application.command.product import ProductCommand
from product_catalog_context.domain.product.product_assignment import CategoryAssignment
from product_catalog_context.infrastructure.sql_alchemy_repository.unit_of_work import SqlAlchemyUnitOfWork

import asyncio
from product_catalog_context.application.product_issue_service import ProductIssueService
from product_catalog_context.domain.product.product_repository import ProductRepository
from product_catalog_context.infrastructure.outbox.repository import OutboxDAO


pytestmark = pytest.mark.usefixtures('insert_data', 'outbox_dispatcher')

@pytest.mark.asyncio
async def test_revert_to_draft_and_delete_tasks(
  product_hierarchy_management_service: CategoryHierarchyManagementService, 
  category_assignment_task_repository: CategoryAssignmentTaskRepository
):
  total_tasks = await category_assignment_task_repository.get_total_in_hierarchy(2)
  assert total_tasks == 2

  await product_hierarchy_management_service.revert_to_draft(2, catalog_manager_id=10)
  hierarchy = await product_hierarchy_management_service.get_hierarchy(2)
  assert hierarchy.status == ProductCategoryHierarchyStatus.DRAFT
  await asyncio.sleep(1)
  total_tasks = await category_assignment_task_repository.get_total_in_hierarchy(2)
  assert total_tasks == 0

@pytest.mark.asyncio
async def test_publish_and_delete_tasks(
  product_hierarchy_management_service: CategoryHierarchyManagementService, 
  category_assignment_task_repository: CategoryAssignmentTaskRepository
):
  total_tasks = await category_assignment_task_repository.get_total_in_hierarchy(2)
  assert total_tasks == 2

  await product_hierarchy_management_service.publish_hierarchy(2, catalog_manager_id=10)
  hierarchy = await product_hierarchy_management_service.get_hierarchy(2)
  assert hierarchy.status == ProductCategoryHierarchyStatus.ACTIVE
  await asyncio.sleep(1)
  total_tasks = await category_assignment_task_repository.get_total_in_hierarchy(2)
  assert total_tasks == 0


@pytest.mark.asyncio
async def test_revert_to_draft_and_change_planned_category_id_category(
  product_hierarchy_management_service: CategoryHierarchyManagementService, 
  product_management_service : ProductManagementService,
  category_assignment_task_repository: CategoryAssignmentTaskRepository
):
  total_tasks = await category_assignment_task_repository.get_total_in_hierarchy(2)
  assert total_tasks == 2
  nutrition_facts = NutritionFacts(reference_quantity=ReferenceQuantity(amount=100, unit='g'), kcal=250, nutrients=Nutrients(fat=120))
  new_info_about_product = ProductCommand(name="Schab Tani", brand_name="Rambert", current_category_id=4, expected_current_category_version=1, planned_category_id=9, nutrition_facts=nutrition_facts, img_src=None)
  await product_management_service.update(2, new_info_about_product, product_editor_id=10)
  await product_hierarchy_management_service.revert_to_draft(2, catalog_manager_id=10)

  hierarchy = await product_hierarchy_management_service.get_hierarchy(2)
  assert hierarchy.status == ProductCategoryHierarchyStatus.DRAFT
  await asyncio.sleep(1)
  total_tasks = await category_assignment_task_repository.get_total_in_hierarchy(2)
  assert total_tasks == 0


