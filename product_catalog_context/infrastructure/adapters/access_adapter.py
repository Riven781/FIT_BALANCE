from identity_and_access_context.public.api.access_api import AccessApi
from product_catalog_context.domain.users import CatalogManager, Moderator, ProductEditor


class AccessAdapter:
  def __init__(self, access_api: AccessApi):
    self.access_api = access_api

  def get_product_editor_for(self, user_id):
    authorized_user = self.access_api.get_authorized_user(user_id, 'product_editor')
    return ProductEditor(authorized_user.user_id)

  def get_catalog_manager_for(self, user_id):
    authorized_user = self.access_api.get_authorized_user(user_id, 'catalog_manager')
    return CatalogManager(authorized_user.user_id)

  def get_moderator_for(self, user_id):
    authorized_user = self.access_api.get_authorized_user(user_id, 'moderator')
    return Moderator(authorized_user.user_id)
  