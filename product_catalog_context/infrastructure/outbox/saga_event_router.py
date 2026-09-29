class SagaEventRouter:
  def __init__(self, saga_router: None):
    self.saga_router = saga_router if saga_router is not None else {}

  def register(self, saga_type, saga):
    self.saga_router[saga_type] = saga

  async def handle(self, event):
    saga_type = getattr(event, 'saga_type', None)
    if saga_type is not None:
      saga = self.saga_router.get(saga_type)
      if saga is not None:
        await saga.handle(event)
