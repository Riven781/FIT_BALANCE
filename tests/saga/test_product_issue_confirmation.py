import pytest
import pytest_asyncio
import asyncio
from product_catalog_context.application.product_issue_service import ProductIssueService
from product_catalog_context.domain.product.product_repository import ProductRepository
from product_catalog_context.infrastructure.outbox.repository import OutboxDAO
from product_catalog_context.domain.issues.product_issue_repository import ProductIssueRepository
from product_catalog_context.domain.issues.product_issue_status import ProductIssueStatus
from product_catalog_context.infrastructure.sql_alchemy_repository.unit_of_work import SqlAlchemyUnitOfWork
from product_catalog_context.infrastructure.sql_alchemy_repository.product_issue import SqlAlchemyProductIssueRepository
from product_catalog_context.infrastructure.sql_alchemy_repository.product_issue_confirmation_saga_repository import SqlAlchemyProductIssueConfirmationSagaRepository
from product_catalog_context.domain.issues.confirmation_saga.saga_status import ProductIssueConfirmationSagaStatus
from product_catalog_context.infrastructure.sql_alchemy_repository.product import SqlAlchemyProductRepository
from product_catalog_context.domain.issues.events import MessageExecutionFailed, ProductIssueConfirmationCancelledAsObsolete, ProductIssueConfirmationStarted, ProductIssueConfirmed, ProductIssueFailed, ProductIssueResetToPending, ResolvedValueAppliedToProduct
from product_catalog_context.domain.issues.confirmation_saga.saga_status import ProductIssueConfirmationSagaStatus
from product_catalog_context.domain.issues.confirmation_saga.commands import ApplyResolvedValueToProduct
from product_catalog_context.application.product_management_service import ProductManagementService
from product_catalog_context.domain.product.nutrition_facts import NutritionFacts, Nutrients, ReferenceQuantity, Nutrients
from product_catalog_context.application.command.product import ProductCommand
from product_catalog_context.domain.repository.errors import UniqueViolationError, ConcurrentModification



@pytest.mark.usefixtures('insert_data', 'event_outbox_dispatcher', 'command_outbox_dispatcher')
@pytest.mark.asyncio
async def test_confirm_issue(product_issue_service: ProductIssueService, product_repository: ProductRepository, outbox_dao: OutboxDAO, product_issue_repository: ProductIssueRepository, session_factory, product_issue_confirmation_saga_repository: SqlAlchemyProductIssueConfirmationSagaRepository):
  await product_issue_service.confirm_issue(issue_id=1, resolved_value=120, moderator_id=100)
  issue = await product_issue_repository.get_by_id(1)
  assert issue.status == ProductIssueStatus.CONFIRMATION_PENDING
  outbox_message = await outbox_dao.get_by_id(1)
  assert outbox_message is not None
  await asyncio.sleep(8)
  product = await product_repository.get_by_id(1)
  assert product.nutrition_facts.kcal == 120
  async with session_factory() as session:
    issue = await SqlAlchemyProductIssueRepository(session).get_by_id(1)
  assert issue.status == ProductIssueStatus.CONFIRMED
  saga = await product_issue_confirmation_saga_repository.get_by_id(99)
  assert saga.status == ProductIssueConfirmationSagaStatus.COMPLETED

@pytest.mark.usefixtures('insert_data', 'event_outbox_dispatcher', 'command_outbox_dispatcher')
@pytest.mark.asyncio
async def test_confirmation_is_cancelled_when_product_value_changed_before_resolution(
  product_issue_service,
  session_factory,
  product_issue_confirmation_saga_repository,
):
  await product_issue_service.confirm_issue(
    issue_id=1,
    resolved_value=120,
    moderator_id=100,
  )
  async with session_factory() as session:
    product_repository = SqlAlchemyProductRepository(session)

    product = await product_repository.get_by_id(1)
    product.change_nutrition_facts(
        product.nutrition_facts.with_updates(kcal=250)
    )
    await session.commit()

    await asyncio.sleep(8)

  async with session_factory() as session:
    issue = await SqlAlchemyProductIssueRepository(session).get_by_id(1)
    product = await SqlAlchemyProductRepository(session).get_by_id(1)

  assert product.nutrition_facts.kcal == 250
  assert issue.status == ProductIssueStatus.OBSOLETE

  saga = await product_issue_confirmation_saga_repository.get_by_id(99)
  assert saga.status == ProductIssueConfirmationSagaStatus.OBSOLETE


@pytest.mark.usefixtures("insert_data")
@pytest.mark.asyncio
async def test_confirmation_waits_when_event_dispatcher_is_not_running(
  product_issue_service,
  session_factory,
  outbox_dao,
):
  await product_issue_service.confirm_issue(
    issue_id=1,
    resolved_value=120,
    moderator_id=100,
  )
  await asyncio.sleep(1)

  async with session_factory() as session:
    issue = await SqlAlchemyProductIssueRepository(session).get_by_id(1)
    product = await SqlAlchemyProductRepository(session).get_by_id(1)

  assert issue.status == ProductIssueStatus.CONFIRMATION_PENDING
  assert product.nutrition_facts.kcal == 300

  message = await outbox_dao.get_by_id(1)

  assert message.message_name == ProductIssueConfirmationStarted.event_type
  assert message.processed_at is None

@pytest.mark.usefixtures("insert_data","event_outbox_dispatcher",)
@pytest.mark.asyncio
async def test_saga_waits_when_command_dispatcher_is_not_running(
  product_issue_service,
  session_factory,
  product_issue_confirmation_saga_repository,
  outbox_dao,
):
  await product_issue_service.confirm_issue(
    issue_id=1,
    resolved_value=120,
    moderator_id=100,
  )
  await asyncio.sleep(3)

  async with session_factory() as session:
    issue = await SqlAlchemyProductIssueRepository(session).get_by_id(1)
    product = await SqlAlchemyProductRepository(session).get_by_id(1)

  assert issue.status == ProductIssueStatus.CONFIRMATION_PENDING
  assert product.nutrition_facts.kcal == 300

  saga = await product_issue_confirmation_saga_repository.get_by_id(99)

  assert saga.status == ProductIssueConfirmationSagaStatus.PRODUCT_UPDATE_PENDING

  messages = await outbox_dao.get_all_messages()

  command = next(
    message
    for message in messages
    if message.message_name == ApplyResolvedValueToProduct.command_type
  )

  assert command.processed_at is None


@pytest.mark.usefixtures("insert_data")
@pytest.mark.asyncio
async def test_confirmation_continues_after_event_dispatcher_restart(
  product_issue_service,
  session_factory,
  start_event_dispatcher,
  start_command_dispatcher,
  db_path
):
  await product_issue_service.confirm_issue(
    issue_id=1,
    resolved_value=120,
    moderator_id=100,
  )

  await asyncio.sleep(1)

  async with session_factory() as session:
    issue = await SqlAlchemyProductIssueRepository(session).get_by_id(1)

  assert issue.status == ProductIssueStatus.CONFIRMATION_PENDING

  event_process = await start_event_dispatcher(db_path)
  command_process = await start_command_dispatcher(db_path)

  await asyncio.sleep(8)

  async with session_factory() as session:
    issue = await SqlAlchemyProductIssueRepository(session).get_by_id(1)
    product = await SqlAlchemyProductRepository(session).get_by_id(1)

  assert issue.status == ProductIssueStatus.CONFIRMED
  assert product.nutrition_facts.kcal == 120

@pytest.mark.usefixtures("insert_data", 'event_outbox_dispatcher', 'command_outbox_dispatcher')
@pytest.mark.asyncio
async def test_product_is_changed_and_confirmation_started_at_the_same_time(
  session_factory,
  outbox_dao: OutboxDAO, fake_access_adapter, message_publisher
):
  product_issue_service = ProductIssueService(SqlAlchemyUnitOfWork(session_factory), fake_access_adapter, message_publisher)
  task1 = product_issue_service.confirm_issue(
    issue_id=1,
    resolved_value=120,
    moderator_id=100,
  )

  nutrition_facts = NutritionFacts(reference_quantity=ReferenceQuantity(amount=100, unit='g'), kcal=140, nutrients=Nutrients(fat=100))
  product_management_service = ProductManagementService(SqlAlchemyUnitOfWork(session_factory), fake_access_adapter, message_publisher)
  task2 = product_management_service.update(1, ProductCommand(name="Schab Drogi", brand_name="Auchan", current_category_id=4, expected_current_category_version=1, planned_category_id=9, expected_planned_category_version=1, nutrition_facts=nutrition_facts, img_src=None, expected_version=1), product_editor_id=10)

  results = await asyncio.gather(task1, task2, return_exceptions=True)

  assert sum(
    isinstance(result, Exception)
    for result in results
  ) == 0

  await asyncio.sleep(10)

  messages = await outbox_dao.get_all_messages()
  for m in messages:
    print(f'id: {m.message_id} type: {m.message_type} message_name: {m.message_name}')

  async with session_factory() as session:
    issue = await SqlAlchemyProductIssueRepository(session).get_by_id(1)
    product = await SqlAlchemyProductRepository(session).get_by_id(1)


  assert issue.status == ProductIssueStatus.OBSOLETE
  assert product.nutrition_facts.kcal == 140



@pytest.mark.usefixtures("insert_data", 'event_outbox_dispatcher', 'command_outbox_dispatcher')
@pytest.mark.asyncio
async def test_two_confirmation_started_at_the_same_time(
  session_factory,
  outbox_dao: OutboxDAO, fake_access_adapter, message_publisher
):
  product_issue_service_1 = ProductIssueService(SqlAlchemyUnitOfWork(session_factory), fake_access_adapter, message_publisher)
  task1 = product_issue_service_1.confirm_issue(
    issue_id=1,
    resolved_value=120,
    moderator_id=100,
  )

  product_issue_service_2 = ProductIssueService(SqlAlchemyUnitOfWork(session_factory), fake_access_adapter, message_publisher)
  task2 = product_issue_service_2.confirm_issue(
    issue_id=1,
    resolved_value=120,
    moderator_id=100,
  )

    
  results = await asyncio.gather(task1, task2, return_exceptions=True)
  print(results)

  assert sum(
    isinstance(result, ConcurrentModification)
    for result in results
  ) == 1
  #one saga will not start because is has old issue version and will rollback (outbox rollback too)
  await asyncio.sleep(8)

  async with session_factory() as session:
    issue = await SqlAlchemyProductIssueRepository(session).get_by_id(1)
    product = await SqlAlchemyProductRepository(session).get_by_id(1)


  assert issue.status == ProductIssueStatus.CONFIRMED
  assert product.nutrition_facts.kcal == 120


@pytest.mark.usefixtures("insert_data", 'event_outbox_dispatcher', 'command_outbox_dispatcher')
@pytest.mark.asyncio
async def test_two_different_confirmation_saga_at_the_same_time(#without product version it goes ok
  session_factory,
  outbox_dao: OutboxDAO, fake_access_adapter, message_publisher
):
  product_issue_service_1 = ProductIssueService(SqlAlchemyUnitOfWork(session_factory), fake_access_adapter, message_publisher)
  task1 = product_issue_service_1.confirm_issue(
    issue_id=1,
    resolved_value=120,
    moderator_id=100,
  )

  product_issue_service_2 = ProductIssueService(SqlAlchemyUnitOfWork(session_factory), fake_access_adapter, message_publisher)
  task2 = product_issue_service_2.confirm_issue(
    issue_id=3,
    resolved_value=10,
    moderator_id=101,
  )

    
  results = await asyncio.gather(task1, task2, return_exceptions=True)

  assert sum(
    isinstance(result, ConcurrentModification)
    for result in results
  ) == 0

  await asyncio.sleep(8)

  async with session_factory() as session:
    issue_kcal = await SqlAlchemyProductIssueRepository(session).get_by_id(1)
    issue_sugars = await SqlAlchemyProductIssueRepository(session).get_by_id(3)

    product = await SqlAlchemyProductRepository(session).get_by_id(1)

  assert issue_kcal.status == ProductIssueStatus.CONFIRMED
  assert issue_sugars.status == ProductIssueStatus.CONFIRMED

  assert product.nutrition_facts.kcal == 120
  assert product.nutrition_facts.nutrients.sugars == 10


@pytest.mark.usefixtures("insert_data", 'event_outbox_dispatcher', 'command_outbox_dispatcher')
@pytest.mark.asyncio
async def test_two_different_confirmation_saga_at_the_same_time_2(
  session_factory,
  outbox_dao: OutboxDAO, fake_access_adapter, message_publisher
):
  product_issue_service_1 = ProductIssueService(SqlAlchemyUnitOfWork(session_factory), fake_access_adapter, message_publisher)
  await product_issue_service_1.confirm_issue(
    issue_id=1,
    resolved_value=120,
    moderator_id=100,
  )

  product_issue_service_2 = ProductIssueService(SqlAlchemyUnitOfWork(session_factory), fake_access_adapter, message_publisher)
  await product_issue_service_2.confirm_issue(
    issue_id=3,
    resolved_value=10,
    moderator_id=101,
  )

  await asyncio.sleep(8)

  async with session_factory() as session:
    issue_kcal = await SqlAlchemyProductIssueRepository(session).get_by_id(1)
    issue_sugars = await SqlAlchemyProductIssueRepository(session).get_by_id(3)
    product = await SqlAlchemyProductRepository(session).get_by_id(1)

  assert issue_kcal.status == ProductIssueStatus.CONFIRMED
  assert issue_sugars.status == ProductIssueStatus.CONFIRMED

  assert product.nutrition_facts.kcal == 120
  assert product.nutrition_facts.nutrients.sugars == 10



@pytest.mark.usefixtures("insert_data")
@pytest.mark.asyncio
async def test_confirmation_saga_when_publisher_doubled_messages(
  session_factory,
  outbox_dao: OutboxDAO, fake_access_adapter, double_message_publisher, start_event_dispatcher, start_command_dispatcher, db_path
):
  event_process = await start_event_dispatcher(db_path, double_messages=True)
  command_process = await start_command_dispatcher(db_path, double_messages=True)
  product_issue_service_1 = ProductIssueService(SqlAlchemyUnitOfWork(session_factory), fake_access_adapter, double_message_publisher)
  await product_issue_service_1.confirm_issue(
    issue_id=1,
    resolved_value=120,
    moderator_id=100,
  )

  await asyncio.sleep(10)

  async with session_factory() as session:
    issue_kcal = await SqlAlchemyProductIssueRepository(session).get_by_id(1)
    product = await SqlAlchemyProductRepository(session).get_by_id(1)

  assert issue_kcal.status == ProductIssueStatus.CONFIRMED


  """  
  messages = await outbox_dao.get_all_messages()
  for m in messages:
      print(f'id: {m.message_id} type: {m.message_type} message_name: {m.message_name} retry_count: {m.retry_count}')
  assert 1 == 0
  """
  assert product.nutrition_facts.kcal == 120

@pytest.mark.usefixtures("insert_data", 'event_outbox_dispatcher', 'command_outbox_dispatcher')
@pytest.mark.asyncio
async def test_6_confirmation_saga_at_the_same_time(
  session_factory,
  outbox_dao: OutboxDAO, fake_access_adapter, message_publisher
):
  product_issue_service_1 = ProductIssueService(SqlAlchemyUnitOfWork(session_factory), fake_access_adapter, message_publisher)
  task1 = product_issue_service_1.confirm_issue(
    issue_id=3,
    resolved_value=120,
    moderator_id=100,
  )

  product_issue_service_2 = ProductIssueService(SqlAlchemyUnitOfWork(session_factory), fake_access_adapter, message_publisher)
  task2 = product_issue_service_2.confirm_issue(
    issue_id=3,
    resolved_value=10,
    moderator_id=101,
  )

  product_issue_service_3 = ProductIssueService(SqlAlchemyUnitOfWork(session_factory), fake_access_adapter, message_publisher)
  task3 = product_issue_service_3.confirm_issue(
    issue_id=3,
    resolved_value=10,
    moderator_id=101,
  )

  product_issue_service_4 = ProductIssueService(SqlAlchemyUnitOfWork(session_factory), fake_access_adapter, message_publisher)
  task4 = product_issue_service_4.confirm_issue(
    issue_id=3,
    resolved_value=12,
    moderator_id=101,
  )

  product_issue_service_5 = ProductIssueService(SqlAlchemyUnitOfWork(session_factory), fake_access_adapter, message_publisher)
  task5 = product_issue_service_5.confirm_issue(
    issue_id=3,
    resolved_value=12,
    moderator_id=101,
  )

  product_issue_service_6 = ProductIssueService(SqlAlchemyUnitOfWork(session_factory), fake_access_adapter, message_publisher)
  task6 = product_issue_service_6.confirm_issue(
    issue_id=3,
    resolved_value=12,
    moderator_id=101,
  )

  results = await asyncio.gather(task1, task2, task3, task4, task5, task6,  return_exceptions=True)

  assert sum(
    isinstance(result, ConcurrentModification)
    for result in results
  ) == 5

  await asyncio.sleep(11)

  async with session_factory() as session:
    issue_sugars = await SqlAlchemyProductIssueRepository(session).get_by_id(3)

  assert issue_sugars.status == ProductIssueStatus.CONFIRMED

