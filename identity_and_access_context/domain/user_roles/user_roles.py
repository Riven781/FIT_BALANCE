from identity_and_access_context.domain.role import Role


class UserRoles:
  def __init__(self, user_id, roles : list[Role], version=None):
    self.user_id = user_id
    self.roles = roles
    self.version = version

  def has_role(self, role):
    return role in self.roles

  def set_roles(self, roles: list[Role]):
    self.roles = roles

  def remove_role(self, role):
    self.roles.remove(role)

  def add_role(self, role):
    if role in self.roles:
      raise ValueError()
    self.roles.append(role)