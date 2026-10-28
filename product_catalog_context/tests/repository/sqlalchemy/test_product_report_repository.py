import pytest
from product_catalog_context.domain.reports.product_report_repository import ProductReportRepository
from product_catalog_context.domain.enums.reported_field import ReportedField
from product_catalog_context.domain.reports.product_report import ProductReport
from product_catalog_context.domain.reports.product_report_item import ProductReportItem
from product_catalog_context.domain.repository.errors import CheckViolationError, ForeignKeyViolationError

pytestmark = pytest.mark.usefixtures('insert_data')

@pytest.mark.asyncio
async def test_get_by_id(product_report_repository: ProductReportRepository):
  report = await product_report_repository.get_by_id(1)
  assert report.report_id == 1
  assert report.product_id == 1
  assert report.user_id == 20
  assert len(report.reported_items) == 2
  item_1 = report.reported_items[0]
  assert item_1.issue_id == 1
  assert item_1.reported_field == ReportedField.KCAL
  assert item_1.proposed_value == '120'
  item_2 = report.reported_items[1]
  assert item_2.issue_id == 2
  assert item_2.reported_field == ReportedField.FAT
  assert item_2.proposed_value is None

@pytest.mark.asyncio
async def test_get_by_id_not_existing_report(product_report_repository: ProductReportRepository):
  report = await product_report_repository.get_by_id(10)
  assert report is None

@pytest.mark.asyncio
async def test_save_new_report(product_report_repository: ProductReportRepository):
  new_report = ProductReport(product_id=1, reported_items=[ProductReportItem(reported_field=ReportedField.SUGARS, issue_id=3)], user_id=6)
  await product_report_repository.save(new_report)
  report = await product_report_repository.get_by_id(new_report.report_id)
  assert report.report_id == new_report.report_id
  assert report.product_id == 1
  assert report.user_id == 6
  assert len(report.reported_items) == 1
  item_1 = report.reported_items[0]
  assert item_1.issue_id == 3
  assert item_1.reported_field == ReportedField.SUGARS
  assert item_1.proposed_value is None

@pytest.mark.asyncio
async def test_save_new_report_with_not_existing_issue(product_report_repository: ProductReportRepository):
  new_report = ProductReport(product_id=1, reported_items=[ProductReportItem(reported_field=ReportedField.SUGARS, issue_id=300)], user_id=6)
  with pytest.raises(ForeignKeyViolationError):
    await product_report_repository.save(new_report)

@pytest.mark.asyncio
async def test_save_existing_report(product_report_repository: ProductReportRepository):
  report = await product_report_repository.get_by_id(2)
  report.add_reported_item(ProductReportItem(reported_field=ReportedField.SUGARS, issue_id=3))
  await product_report_repository.save(report)
  updated_report = await product_report_repository.get_by_id(2)
  assert updated_report.product_id == 1
  assert updated_report.user_id == 10
  assert len(report.reported_items) == 2
  item_1 = report.reported_items[0]
  assert item_1.issue_id == 1
  assert item_1.reported_field == ReportedField.KCAL
  assert item_1.proposed_value == '120'
  item_2 = report.reported_items[1]
  assert item_2.issue_id == 3
  assert item_2.reported_field == ReportedField.SUGARS
  assert item_2.proposed_value is None

@pytest.mark.asyncio
async def test_delete_report(product_report_repository: ProductReportRepository, db_session):
  report = await product_report_repository.get_by_id(1)
  await product_report_repository.delete(report)
  await db_session.commit()
  report = await product_report_repository.get_by_id(1)
  assert report is None