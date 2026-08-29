from enum import StrEnum


class Role(StrEnum):
  CATALOG_MANAGER = 'catalog_manager'
  PRODUCT_EDITOR = 'product_editor'
  MODERATOR = 'moderator'
  ADMIN = 'admin'
  USER = 'user'