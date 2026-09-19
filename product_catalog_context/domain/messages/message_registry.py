class MessageRegistry:
  def __init__(self):
    self.message_type_by_name = {}

  def register(self, message_name, message_class):
    self.message_type_by_name[message_name] = message_class

  def get(self, message_name):
    return self.message_type_by_name[message_name]