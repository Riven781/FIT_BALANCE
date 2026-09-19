from product_catalog_context.domain.messages.message import DomainCommand
from product_catalog_context.domain.messages.message_bus import MessageBus


class CommandBus(MessageBus):
  def __init__(self):
    self.handlers = {}

  def register(self, command_type, handler):
    if command_type in self.handlers:
      raise RuntimeError('Command can only have one handler')
    self.handlers[command_type] = handler
    
  async def dispatch(self, command: DomainCommand):
    handler = self.handlers[command.command_type]
    await handler.handle(command)