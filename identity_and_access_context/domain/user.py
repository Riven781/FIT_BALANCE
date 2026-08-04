class User:
  def __init__(self, username, encrypted_password, email, roles):
    self.username = username
    self.encrypted_password = encrypted_password
    self.email = email
    self.roles = roles

  def change_password(self, encrypted_password):
    self.encrypted_password = encrypted_password

  def remove_role(self, role):
    self.roles.remove(role)

  def add_role(self, role):
    if role in self.roles:
      raise ValueError()
    self.roles.append(role)