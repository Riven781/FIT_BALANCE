from dataclasses import dataclass


@dataclass
class RegisterCommand:
  username: str
  password: str
  password_repeated: str
  email: str