from datetime import datetime, timezone

from identity_and_access_context.domain.refresh_token.errors import RefreshTokenAlreadyRevoked, RefreshTokenExpired


class RefreshToken:
  def __init__(self, token_hash, user_id, expires_at, created_at=None, token_id = None, revoked_at = None):
    self.token_id = token_id
    self.token_hash = token_hash
    self.user_id = user_id
    self.expires_at = expires_at
    self.revoked_at = revoked_at
    self.created_at = created_at

  def revoke(self):
    if self.revoke is not None:
      raise RefreshTokenAlreadyRevoked()
    self.revoked_at = datetime.now(timezone.utc)

  def ensure_valid(self):
    if self.revoked_at is not None:
      raise RefreshTokenAlreadyRevoked

    if self.expires_at <= datetime.now(timezone.utc):
      raise RefreshTokenExpired()

