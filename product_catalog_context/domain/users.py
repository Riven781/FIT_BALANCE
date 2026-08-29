from dataclasses import dataclass


@dataclass
class User:
  user_id: int


@dataclass
class ProductEditor(User):
  pass

@dataclass
class CatalogManager(User):
  pass

@dataclass
class Moderator(User):
  pass