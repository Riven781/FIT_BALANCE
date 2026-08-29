from dataclasses import dataclass
from identity_and_access_context.domain.auth_method import AuthMethod
from identity_and_access_context.domain.role import Role


class Session:
  def __init__(self, session_id, session_data: "SessionData", ttl=60 * 60 * 24 * 7):
    self.session_id = session_id
    self.session_data = session_data
    self.ttl = ttl

  def increase_ttl(self, seconds):
    self.ttl += seconds

@dataclass
class SessionData:
  user_id: int
  username : str