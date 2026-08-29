from dataclasses import dataclass
from enum import StrEnum

class AuthMethod(StrEnum):
  JWT = 'jwt'
  SESSION = 'session'

@dataclass 
class RawAuthenticationCredentials:
  #auth_method : AuthMethod
  session_id: str | None
  token: str | None
