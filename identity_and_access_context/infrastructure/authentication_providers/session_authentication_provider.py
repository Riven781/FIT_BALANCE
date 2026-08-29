from identity_and_access_context.domain.authentication_provider.authentication_provider import AuthenticationProvider
from identity_and_access_context.domain.authentication_provider.errors import CredentialNotFound
from identity_and_access_context.domain.session.session import Session, SessionData


class SessionAuthenticationProvider(AuthenticationProvider):
  def __init__(self, session_repository):
    self.session_repository = session_repository

  async def login(self, user) -> Session:
    session_id = self.session_repository.next_id()
    session = Session(session_id = session_id, session_data=SessionData(username=user.username, user_id=user.user_id), ttl=60 * 60 * 24 * 30 )
    await self.session_repository.save(session)
    return session

  async def logout(self, session_id):
    session = await self.session_repository.get_by_id(session_id)
    if session is None:
      raise CredentialNotFound()
    await self.session_repository.delete_by_id(session_id)

  async def authenticate(self, session_id) -> int | None:
    session = await self.session_repository.get_by_id(session_id)
    if session is None:
      raise CredentialNotFound()
    return session.session_data.user_id

  async def refresh(self, session_id):
    session = await self.session_repository.get_by_id(session_id)
    if session is None:
      raise CredentialNotFound()
    session.increase_ttl(60 * 60 * 24 * 30)
    await self.session_repository.save(session)
    return session
    #Set-Cookie: session_id=abc; Max-Age=604800; HttpOnly; Secure
