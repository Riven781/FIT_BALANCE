import pytest
from product_catalog_context.infrastructure.aiosqlite_repository.product_report_repository import ProductReportRepository
from product_catalog_context.domain.enums.reported_field import ReportedField
from product_catalog_context.domain.reports.product_report import ProductReport
from product_catalog_context.domain.reports.product_report_item import ProductReportItem

async def insert_reports(db):
  cursor = await db.executescript(
    """
    INSERT INTO Product (id, name, brand_name, kcal, reference_amount, reference_unit, name_search_standard)
    VALUES 
    (1, "Schab Drogi", "Auchan", 300, 100, "g","schab drogi"),
    (2, "Schab Tani", "Rambert", 250, 100, "g", "schab tani");

    INSERT INTO ProductIssue (id, product_id, reported_field, status, resolved_value)
      VALUES 
      (1, 1, 'kcal', 'pending', NULL),
      (2, 1, 'fat', 'pending', NULL),
      (3, 2, 'kcal', 'pending', NULL),
      (4, 2, 'sugars', 'pending', NULL), 
      (5, 2, 'carbohydrates', 'pending', NULL);


    INSERT INTO ProductReport (id, product_id)
    VALUES 
    (1, 1), (2, 2);

    INSERT INTO ProductReportItem (id, report_id, issue_id, proposed_value) VALUES
    (1, 1, 1, NULL),
    (2, 1, 2, 20),
    (3, 2, 3, 120);
    """
  )
  await db.commit()
  await cursor.close()

@pytest.mark.asyncio
async def test_get_by_id(db):
  await insert_reports(db)
  repo = ProductReportRepository(db)
  report = await repo.get_by_id(1)
  assert report.report_id == 1
  assert report.product_id == 1
  assert len(report.reported_items) == 2
  reported_item_1 = report.reported_items[0]
  assert reported_item_1.reported_field == ReportedField.KCAL
  assert reported_item_1.issue_id == 1
  assert reported_item_1.proposed_value is None
  reported_item_2 = report.reported_items[1]
  assert reported_item_2.reported_field == ReportedField.FAT
  assert reported_item_2.issue_id == 2
  assert reported_item_2.proposed_value == '20'

@pytest.mark.asyncio
async def test_get_by_not_existing_id(db):
  await insert_reports(db)
  repo = ProductReportRepository(db)
  report = await repo.get_by_id(100)
  assert report is None

@pytest.mark.asyncio
async def test_insert_product_report_with_1_item(db):
  await insert_reports(db)
  repo = ProductReportRepository(db)
  item_1 = ProductReportItem(reported_field=ReportedField.SUGARS, proposed_value=10, issue_id=4)
  product_report = ProductReport(product_id=2, reported_items=[item_1])
  report_id = await repo.insert(product_report)
  report = await repo.get_by_id(report_id)
  assert report.report_id == report_id
  assert report.product_id == 2
  assert len(report.reported_items) == 1
  reported_item_1 = report.reported_items[0]
  assert reported_item_1.reported_field == ReportedField.SUGARS
  assert reported_item_1.issue_id == 4
  assert reported_item_1.proposed_value == '10'

@pytest.mark.asyncio
async def test_insert_product_report_with_2_item(db):
  await insert_reports(db)
  repo = ProductReportRepository(db)
  item_1 = ProductReportItem(reported_field=ReportedField.SUGARS, proposed_value=10, issue_id=4)
  item_2 = ProductReportItem(reported_field=ReportedField.CARBOHYDRATES, proposed_value=None, issue_id=5)
  product_report = ProductReport(product_id=2, reported_items=[item_1, item_2])
  report_id = await repo.insert(product_report)
  report = await repo.get_by_id(report_id)
  assert report.report_id == report_id
  assert report.product_id == 2
  assert len(report.reported_items) == 2
  reported_item_1 = report.reported_items[0]
  assert reported_item_1.reported_field == ReportedField.SUGARS
  assert reported_item_1.issue_id == 4
  assert reported_item_1.proposed_value == '10'
  reported_item_1 = report.reported_items[1]
  assert reported_item_1.reported_field == ReportedField.CARBOHYDRATES
  assert reported_item_1.issue_id == 5
  assert reported_item_1.proposed_value is None