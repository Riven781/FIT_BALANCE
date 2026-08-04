from identity_and_access_context.domain.services.authenticate import authenticate


class AuthenticateService:
  def __init__(self, user_repository):
    self.user_repository = user_repository

  def login(self, username, password):
    user = authenticate(username, password, self.user_repository)
    if user is None:
      pass



  def register(self):
    pass