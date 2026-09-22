import argparse

from product_catalog_context.application.product_issue_confirmation.apply_resolved_value_to_product_handler import ApplyResolvedValueToProductHandler
from product_catalog_context.application.product_issue_confirmation.cancel_product_issue_confirmation import CancelProductIssueConfirmationHandler
from product_catalog_context.application.product_issue_confirmation.confirm_product_issue_handler import ConfirmProductIssueHandler
from product_catalog_context.application.product_issue_confirmation.reset_product_issue_to_pending_handler import ResetProductIssueToPendingHandler
from product_catalog_context.domain.issues.confirmation_saga.commands import ApplyResolvedValueToProduct, CancelProductIssueConfirmation, ConfirmProductIssue, ResetProductIssueToPending
from product_catalog_context.domain.messages.command_bus import CommandBus
from product_catalog_context.domain.messages.domain_message_publisher import DomainMessagePublisher
from product_catalog_context.domain.messages.message_registry import MessageRegistry
from product_catalog_context.domain.messages.message_serializer import MessageSerializer
from product_catalog_context.infrastructure.outbox.message_dispatcher import MessageOutboxDispatcher
from product_catalog_context.infrastructure.outbox.repository import OutboxDAO
import asyncio

from product_catalog_context.infrastructure.outbox.subscriber import OutboxSubscriber
from product_catalog_context.infrastructure.outbox.test_session_factory import get_session_factory
from product_catalog_context.infrastructure.sql_alchemy_repository.unit_of_work import SqlAlchemyUnitOfWorkFactory


class OutboxCommandDispatcher(MessageOutboxDispatcher):
  def __init__(self, session_factory, command_bus: CommandBus, message_serializer: MessageSerializer, test = False, sync=False):
    super().__init__(session_factory, test)
    self.command_bus = command_bus
    self.message_serializer = message_serializer

  async def pull_messages(self):
    async with self.session_factory() as session:
      outbox_dao = OutboxDAO(session)
      unprocessed_message_ids = await outbox_dao.get_unprocessed_command_ids(limit=50)
      return unprocessed_message_ids

  async def handle(self, message_id):
    try:
      async with self.session_factory() as session:
        outbox_repository = OutboxDAO(session=session)
        message = await outbox_repository.get_by_id(message_id)
      message = self.message_serializer.deserialize(message_name=message.message_name, payload=message.payload)
      await self.command_bus.dispatch(message)
    except Exception as e:
      await self._handle_errors(message_id=message_id, e=e)
      return
    await self._process_message(message_id)


def parse_args():
  parser = argparse.ArgumentParser()
  parser.add_argument('--database-url', required=True)
  return parser.parse_args()

if __name__ == '__main__':
  args = parse_args()
  subscriber = OutboxSubscriber()
  publisher = DomainMessagePublisher()
  publisher.global_subscribe(subscriber)

  command_bus = CommandBus()
  
  session_factory = get_session_factory(args.database_url)
  unit_of_work_factory = SqlAlchemyUnitOfWorkFactory(session_factory)
  command_bus.register(ApplyResolvedValueToProduct, ApplyResolvedValueToProductHandler(unit_of_work_factory, publisher))
  command_bus.register(CancelProductIssueConfirmation, CancelProductIssueConfirmationHandler(unit_of_work_factory, publisher))
  command_bus.register(ConfirmProductIssue, ConfirmProductIssueHandler(unit_of_work_factory, publisher))
  command_bus.register(ResetProductIssueToPending, ResetProductIssueToPendingHandler(unit_of_work_factory, publisher))



  registry = MessageRegistry()
  registry.register(ApplyResolvedValueToProduct.command_type, ApplyResolvedValueToProduct)
  registry.register(CancelProductIssueConfirmation.command_type, CancelProductIssueConfirmation)
  registry.register(ConfirmProductIssue.command_type, ConfirmProductIssue)
  registry.register(ResetProductIssueToPending.command_type, ResetProductIssueToPending)


  dispatcher = OutboxCommandDispatcher(get_session_factory(args.database_url), command_bus, MessageSerializer(registry), sync=False)
  asyncio.run(dispatcher.run())