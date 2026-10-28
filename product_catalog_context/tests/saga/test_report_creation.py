import asyncio

import pytest
from sqlalchemy import text

from product_catalog_context.application.command.product_report import ProductReportCommand, ReportedItem
from product_catalog_context.application.errors.errors import ProductReportExistsForThisVersion
from product_catalog_context.application.product_report_service import ProductReportService
from product_catalog_context.domain.enums.reported_field import ReportedField
from product_catalog_context.domain.reports.product_report_item_status import ProductReportItemStatus
from product_catalog_context.domain.repository.errors import UniqueViolationError
from product_catalog_context.infrastructure.sql_alchemy_repository.product_issue import SqlAlchemyProductIssueRepository
from product_catalog_context.infrastructure.sql_alchemy_repository.product_report import SqlAlchemyProductReportRepository

#pytest tests/saga/test_report_creation.py
pytestmark = pytest.mark.usefixtures('insert_data', 'event_outbox_dispatcher')

@pytest.mark.asyncio
async def test_create_product_report_with_new_issues(product_report_service: ProductReportService, session_factory):
  product_command = ProductReportCommand(
    product_id=3, 
    reported_items=[
      ReportedItem(reported_field=ReportedField.KCAL, proposed_value=10, old_value=400), 
      ReportedItem(reported_field=ReportedField.FAT, old_value=90.0),
      ReportedItem(reported_field=ReportedField.NAME, old_value='Schab Średni')

    ]
  )
  report = await product_report_service.create_report(product_command, user_id=10)


  await asyncio.sleep(1)

  async with session_factory() as session:
    issue_kcal = await SqlAlchemyProductIssueRepository(session).get_pending_issue_by_reported_value(product_id=3, reported_field=ReportedField.KCAL, old_value=400)
    issue_fat = await SqlAlchemyProductIssueRepository(session).get_pending_issue_by_reported_value(product_id=3, reported_field=ReportedField.FAT, old_value='90.0')
    issue_name = await SqlAlchemyProductIssueRepository(session).get_pending_issue_by_reported_value(product_id=3, reported_field=ReportedField.NAME, old_value='Schab Średni')
    report = await SqlAlchemyProductReportRepository(session).get_by_id(report.report_id)

  item_kcal = report.get_report_item(ReportedField.KCAL)
  assert item_kcal.proposed_value == '10'
  assert item_kcal.issue_id == issue_kcal.issue_id
  assert issue_kcal is not None
  assert issue_fat is not None
  assert issue_name is not None

  assert issue_kcal.old_value == 400
  assert issue_kcal.reported_field == ReportedField.KCAL

  item_fat = report.get_report_item(ReportedField.FAT)
  assert item_fat.issue_id == issue_fat.issue_id
  assert issue_fat.old_value == 90.0
  assert issue_fat.reported_field == ReportedField.FAT

  item_name = report.get_report_item(ReportedField.NAME)
  assert item_name.issue_id == issue_name.issue_id
  assert issue_name.old_value == 'Schab Średni'
  assert issue_name.reported_field == ReportedField.NAME

@pytest.mark.asyncio
async def test_create_product_report_with_existing_issue(product_report_service: ProductReportService, session_factory):
  product_command = ProductReportCommand(
    product_id=1, 
    reported_items=[
      ReportedItem(reported_field=ReportedField.KCAL, proposed_value=10, old_value=300), 
    ]
  )
  report = await product_report_service.create_report(product_command, user_id=11)
  await asyncio.sleep(1)

  async with session_factory() as session:
    issue_kcal = await SqlAlchemyProductIssueRepository(session).get_pending_issue_by_reported_value(product_id=1, reported_field=ReportedField.KCAL, old_value=300)
    report = await SqlAlchemyProductReportRepository(session).get_by_id(report.report_id)

  item_kcal = report.get_report_item(ReportedField.KCAL)
  assert item_kcal.issue_id == 1
  assert report.report_id is not None
  assert issue_kcal is not None
  assert issue_kcal.issue_id == 1
  assert issue_kcal.old_value == 300

@pytest.mark.asyncio
async def test_create_product_report_with_with_existing_product_version(product_report_service: ProductReportService, session_factory):
  product_command = ProductReportCommand(
    product_id=1, 
    reported_items=[
      ReportedItem(reported_field=ReportedField.KCAL, proposed_value=10, old_value=300), 
    ]
  )
  with pytest.raises(ProductReportExistsForThisVersion):
    report = await product_report_service.create_report(product_command, user_id=10)

@pytest.mark.asyncio
async def test_create_product_report_with_new_issue_two_times_by_different_users(unit_of_work_factory, fake_access_adapter, message_publisher, session_factory):
  product_command = ProductReportCommand(
    product_id=3, 
    reported_items=[
      ReportedItem(reported_field=ReportedField.KCAL, proposed_value=10, old_value=400), 
    ]
  )

  service1 = ProductReportService(unit_of_work_factory.create(), fake_access_adapter, message_publisher)
  service2 = ProductReportService(unit_of_work_factory.create(), fake_access_adapter, message_publisher)
  task1 = service1.create_report(product_command, 10)
  task2 = service2.create_report(product_command, 11)

  results = await asyncio.gather(task1, task2, return_exceptions=True)
  report_1 = results[0]
  report_2 = results[1]

  await asyncio.sleep(1)

  async with session_factory() as session:
    report_1 = await  SqlAlchemyProductReportRepository(session).get_by_id(report_1.report_id)
    report_2 = await  SqlAlchemyProductReportRepository(session).get_by_id(report_2.report_id)

    issue_kcal = await SqlAlchemyProductIssueRepository(session).get_pending_issue_by_reported_value(product_id=3, reported_field=ReportedField.KCAL, old_value=400)

  assert report_1.get_report_item(ReportedField.KCAL).issue_id == issue_kcal.issue_id
  assert report_2.get_report_item(ReportedField.KCAL).issue_id == issue_kcal.issue_id


@pytest.mark.asyncio
async def test_create_product_report_with_outdated_old_value(product_report_service: ProductReportService, session_factory):
  product_command = ProductReportCommand(
    product_id=3, 
    reported_items=[
      ReportedItem(reported_field=ReportedField.KCAL, proposed_value=10, old_value=101), #in  data kcal = 400
    ]
  )
  report = await product_report_service.create_report(product_command, user_id=10)


  await asyncio.sleep(1)

  async with session_factory() as session:
    issue_kcal = await SqlAlchemyProductIssueRepository(session).get_pending_issue_by_reported_value(product_id=3, reported_field=ReportedField.KCAL, old_value=400)
    report = await  SqlAlchemyProductReportRepository(session).get_by_id(report.report_id)

  assert issue_kcal is None
  assert report.get_report_item(ReportedField.KCAL).status == ProductReportItemStatus.OUTDATED