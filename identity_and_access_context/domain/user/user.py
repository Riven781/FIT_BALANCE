class User:
  def __init__(self, username, hashed_password, email, user_id = None):
    self.user_id = user_id
    self.username = username
    self.hashed_password = hashed_password
    self.email = email

  def change_password(self, hashed_password):
    self.hashed_password = hashed_password

