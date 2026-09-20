import pytest
import pytest_asyncio
import asyncio
from product_catalog_context.application.product_management_service import ProductManagementService
from product_catalog_context.application.command.product import ProductCommand
from product_catalog_context.domain.product.nutrition_facts import NutritionFacts, Nutrients, ReferenceQuantity, Nutrients
from product_catalog_context.infrastructure.sql_alchemy_repository.product_issue import SqlAlchemyProductIssueRepository
from product_catalog_context.domain.issues.product_issue_status import ProductIssueStatus

from product_catalog_context.application.product_issue_service import ProductIssueService
from product_catalog_context.domain.product.product_repository import ProductRepository
from product_catalog_context.infrastructure.outbox.repository import OutboxDAO


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
  await asyncio.sleep(10)
  product = await product_management_service.get(1)
  assert product.kcal == 210
  issue_kcal = await product_issue_repository.get_by_id(1)
  assert issue_kcal.status == ProductIssueStatus.OBSOLETE
  issue_sugars = await product_issue_repository.get_by_id(3)
  assert issue_sugars.status == ProductIssueStatus.OBSOLETE
  issue_fat = await product_issue_repository.get_by_id(2)
  assert issue_fat.status == ProductIssueStatus.CONFIRMED