import json

from product_catalog_context.domain.messages.message import DomainMessage
from product_catalog_context.domain.messages.message_registry import MessageRegistry


class MessageSerializer:
  def __init__(self, registry: MessageRegistry):
    self.registry = registry
    
  def deserialize(self, message_name, payload):
    cls = self.registry.get(message_name)
    payload = json.loads(payload)
    return cls(**payload)
