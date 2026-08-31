import hashlib
import secrets

import jwt
import json
from config import JWT_SECRET
from datetime import datetime, timedelta, timezone

from identity_and_access_context.application.unit_of_work.unit_of_work import UnitOfWork
from identity_and_access_context.domain.authentication_provider.authentication_provider import AuthenticationProvider
from identity_and_access_context.domain.authentication_provider.errors import CredentialNotFound, InvalidCredential
from identity_and_access_context.domain.refresh_token.errors import RefreshTokenAlreadyRevoked, RefreshTokenExpired
from identity_and_access_context.domain.refresh_token.refresh_token import RefreshToken
from identity_and_access_context.domain.session.session import SessionData
from identity_and_access_context.domain.tokens import Tokens
from identity_and_access_context.infrastructure.security import hash_value

class JwtAuthenticationProvider(AuthenticationProvider):
  def __init__(self, unit_of_work: UnitOfWork):
    self.unit_of_work = unit_of_work

  async def login(self, user) -> Tokens:
    async with self.unit_of_work:
      access_token = self._create_access_token(user.user_id)
      refresh_token = await self._create_refresh_token(user.user_id)
      return Tokens(access_token, refresh_token)

  async def logout(self, refresh_token): #refresh token 
    async with self.unit_of_work:
      token_hash = hash_value(refresh_token)
      refresh_token = await self.unit_of_work.refresh_tokens.get_by_hash(token_hash)
      if refresh_token is not None:
        await self.unit_of_work.refresh_tokens.delete(refresh_token)

  async def authenticate(self, access_token) -> int: #user_id
    payload = self._decode_access_token(access_token)
    return int(payload['sub'])

  async def refresh(self, refresh_token_value):
    async with self.unit_of_work:
      token_hash = hash_value(refresh_token_value)
      refresh_token = await self.unit_of_work.refresh_tokens.get_by_hash(token_hash)
      if refresh_token is None:
        raise CredentialNotFound("Refresh Token not found")
      try:
        refresh_token.ensure_valid()
      except (RefreshTokenAlreadyRevoked, RefreshTokenExpired) as e:
        raise InvalidCredential("Invalid Refresh Token") from e

      access_token = self._create_access_token(refresh_token.user_id)
      now = datetime.now(timezone.utc)
      if refresh_token.expires_at < now + timedelta(days=7):
        await self.unit_of_work.refresh_tokens.delete(refresh_token)
        new_refresh_token_value = await self._create_refresh_token(refresh_token.user_id)
        return Tokens(access_token, new_refresh_token_value)
      return Tokens(access_token, refresh_token_value)
    
  def _create_access_token(self, user_id, seconds=60 * 30):
    now = datetime.now(timezone.utc)
    token = jwt.encode({
      'sub' : str(user_id),
      'iat' : now,
      'exp' : now + timedelta(seconds=seconds)
    }, JWT_SECRET, algorithm="HS256")
    return token

  def _decode_access_token(self, token):
    try:
      payload = jwt.decode(token, JWT_SECRET, algorithms='HS256')
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
      raise InvalidCredential() from e
    return payload

  async def _create_refresh_token(self, user_id, seconds=60  * 60 * 24* 30):
    now = datetime.now(timezone.utc)
    refresh_token_value = secrets.token_urlsafe(32)
    token_hash = hash_value(refresh_token_value)
    refresh_token = RefreshToken(token_hash=token_hash, user_id=user_id, expires_at=now + timedelta(seconds=seconds), created_at=now)
    await self.unit_of_work.refresh_tokens.save(refresh_token)
    return refresh_token_value
