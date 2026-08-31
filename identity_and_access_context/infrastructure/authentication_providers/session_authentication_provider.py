from identity_and_access_context.application.unit_of_work.unit_of_work import UnitOfWork
from identity_and_access_context.domain.authentication_provider.authentication_provider import AuthenticationProvider
from identity_and_access_context.domain.authentication_provider.errors import CredentialNotFound
from identity_and_access_context.domain.session.session import Session, SessionData


class SessionAuthenticationProvider(AuthenticationProvider):
  def __init__(self, unit_of_work: UnitOfWork):
    self.unit_of_work = unit_of_work

  async def login(self, user) -> Session:
    async with self.unit_of_work:
      session_id = self.unit_of_work.sessions.next_id()
      session = Session(session_id = session_id, session_data=SessionData(username=user.username, user_id=user.user_id), ttl=60 * 60 * 24 * 30 )
      await self.unit_of_work.sessions.save(session)
      return session

  async def logout(self, session_id):
    async with self.unit_of_work:
      session = await self.unit_of_work.sessions.get_by_id(session_id)
      if session is None:
        raise CredentialNotFound()
      await self.unit_of_work.sessions.delete_by_id(session_id)

  async def authenticate(self, session_id) -> int | None:
    async with self.unit_of_work:
      session = await self.unit_of_work.sessions.get_by_id(session_id)
      if session is None:
        raise CredentialNotFound()
      return session.session_data.user_id

  async def refresh(self, session_id):
    async with self.unit_of_work:
      session = await self.unit_of_work.sessions.get_by_id(session_id)
      if session is None:
        raise CredentialNotFound()
      session.increase_ttl(60 * 60 * 24 * 30)
      await self.unit_of_work.sessions.save(session)
      return session
    #Set-Cookie: session_id=abc; Max-Age=604800; HttpOnly; Secure
