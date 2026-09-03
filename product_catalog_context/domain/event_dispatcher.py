class EventDispatcher:
  def __init__(self):
    self.handlers = {}

  def register(self, event_type, handler):
    self.handlers[event_type] = handler

  async def dispatch(self, events):
    for event in events:
      handler = self.handlers[type(event)]
      await handler.handle(event)