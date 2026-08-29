from dataclasses import dataclass


@dataclass
class Tokens:
  access_token: str
  refresh_token: str