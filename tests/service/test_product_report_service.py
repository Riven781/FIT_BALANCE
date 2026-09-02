import pytest
from product_catalog_context.application.command.product_report import ProductReportCommand, ReportedItem
from product_catalog_context.domain.enums.reported_field import ReportedField
from product_catalog_context.application.product_report_service import ProductReportService
from product_catalog_context.domain.enums.product_issue_status import ProductIssueStatus


@pytest.mark.asyncio
async def test_create_report_without_issues(product_report_service : ProductReportService, db):
  product_report_command = ProductReportCommand(product_id=1, reported_items=[ReportedItem(reported_field=ReportedField.KCAL), ReportedItem(reported_field=ReportedField.FIBER)])
  product_report = await product_report_service.create_report(product_report_command, 1)
  assert product_report.product_id == 1
  assert len(product_report.reported_items) == 2
  product_item_1 = product_report.reported_items[0]
  assert product_item_1.reported_field == ReportedField.KCAL
  assert product_item_1.proposed_value is None
  assert product_item_1.issue_id is not None
  product_item_2 = product_report.reported_items[1]
  assert product_item_2.reported_field == ReportedField.FIBER
  assert product_item_2.proposed_value is None
  assert product_item_2.issue_id is not None

  async with db.execute("""
    SELECT * FROM ProductIssue WHERE id = ?
  """, (product_item_1.issue_id,)) as cursor:
    issue = await cursor.fetchone()
  assert issue['reported_field'] == ReportedField.KCAL
  assert issue['product_id'] == 1
  assert issue['status'] == ProductIssueStatus.PENDING

  async with db.execute("""
    SELECT * FROM ProductIssue WHERE id = ?
  """, (product_item_2.issue_id,)) as cursor:
    issue = await cursor.fetchone()
  assert issue['reported_field'] == ReportedField.FIBER
  assert issue['product_id'] == 1
  assert issue['status'] == ProductIssueStatus.PENDING

  
@pytest.mark.asyncio
async def test_create_report_with_issue(product_report_service : ProductReportService, db):
  product_report_command = ProductReportCommand(product_id=1, reported_items=[ReportedItem(reported_field=ReportedField.SUGARS, proposed_value=11), ReportedItem(reported_field=ReportedField.FIBER)])
  product_report = await product_report_service.create_report(product_report_command, 1)
  assert product_report.product_id == 1
  assert len(product_report.reported_items) == 2
  product_item_1 = product_report.reported_items[0]
  assert product_item_1.reported_field == ReportedField.SUGARS
  assert product_item_1.proposed_value == 11
  assert product_item_1.issue_id == 100
  product_item_2 = product_report.reported_items[1]
  assert product_item_2.reported_field == ReportedField.FIBER
  assert product_item_2.proposed_value is None
  assert product_item_2.issue_id is not None

  async with db.execute("""
    SELECT * FROM ProductIssue WHERE id = ? AND status='pending'
  """, (product_item_1.issue_id,)) as cursor:
    issue = await cursor.fetchone()
  assert issue['id'] == 100
  assert issue['reported_field'] == ReportedField.SUGARS
  assert issue['product_id'] == 1
  assert issue['status'] == ProductIssueStatus.PENDING

  async with db.execute("""
    SELECT * FROM ProductIssue WHERE id = ?
  """, (product_item_2.issue_id,)) as cursor:
    issue = await cursor.fetchone()
  assert issue['reported_field'] == ReportedField.FIBER
  assert issue['product_id'] == 1
  assert issue['status'] == ProductIssueStatus.PENDING