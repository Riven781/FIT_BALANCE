from enum import StrEnum


class AuthMethod(StrEnum):
  SESSION = 'session'
  JWT = 'jwt'