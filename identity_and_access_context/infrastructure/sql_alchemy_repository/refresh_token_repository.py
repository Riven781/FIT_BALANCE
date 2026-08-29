from sqlalchemy import select

from identity_and_access_context.domain.refresh_token.refresh_token import RefreshToken
from identity_and_access_context.domain.refresh_token.refresh_token_repository import RefreshTokenRepository
from identity_and_access_context.infrastructure.sql_alchemy_repository.sql_alchemy_repository import BaseSqlAlchemyRepository
from datetime import datetime, timezone

class SqlAlchemyRefreshTokenRepository(RefreshTokenRepository, BaseSqlAlchemyRepository):
  def __init__(self, session):
    super().__init__(session)

  async def get_by_id(self, token_id):
    return await self.session.get(RefreshToken, token_id)

  async def get_by_hash(self, token_hash):
    stmt = (select(RefreshToken)
      .where(RefreshToken.token_hash == token_hash)
    )
    result = await self.session.execute(stmt)
    refresh_token =  result.scalar_one_or_none()
    if refresh_token is None:
      return None
    refresh_token.expires_at = refresh_token.expires_at.replace(tzinfo=timezone.utc)
    return refresh_token

  async def delete(self, token):
    await self.session.delete(token)

  async def save(self, token: RefreshToken):
    await self._save(token)
