import json
from identity_and_access_context.domain.session.session_repository import SessionRepository
from identity_and_access_context.domain.session.session import Session, SessionData
import secrets

class RedisSessionRepository(SessionRepository):
  def __init__(self, redis_client):
    self._redis = redis_client

  async def save(self, session: Session):
    session_key = f'session:{session.session_id}'
    user_sessions_key = f'user_sessions:{session.session_data.user_id}'
    async with self._redis.pipeline(transaction=True) as pipe:
      pipe.hset(
        session_key,
        mapping={
          'user_id': session.session_data.user_id, 
          'username': session.session_data.username
          })
      pipe.expire(session_key,  session.ttl,  gt=True)
      pipe.sadd(user_sessions_key, session.session_id)
      pipe.expire(user_sessions_key, session.ttl, gt=True)
      await pipe.execute()

  async def get_by_id(self, session_id):
    session_key = f'session:{session_id}'
    data = await self._redis.hgetall(session_key)
    if not data:
      return None
    ttl = await self._redis.ttl(session_key)    
    return Session(session_id=session_id, session_data=SessionData(username=data['username'], user_id=int(data['user_id'])), ttl=ttl)

  async def get_all_by_user_id(self, user_id): #nessesery if admin chane roles
    user_sessions_key = f"user_sessions:{user_id}"
    session_ids = await self._redis.smembers(user_sessions_key)
    async with self._redis.pipeline(transaction=False) as pipe:
      for session_id in session_ids:
        pipe.hgetall(f'session:{session_id}')
      results = await pipe.execute()

      active_sessions = []
      expired_sessions = []

      for s_id, session_data in zip(session_ids, results):
        if session_data:
          ttl = await self._redis.ttl(f'session:{s_id}')
          active_sessions.append(Session(session_id=s_id, session_data=SessionData(username=session_data['username'], user_id=int(session_data['user_id'])), ttl=ttl))
        else:
          expired_sessions.append(s_id)

      if expired_sessions:
        await self._redis.srem(user_sessions_key, *expired_sessions)
    return active_sessions

  async def get_all_by_session_id(self, session_id): #nessesery if user changed username
    session_key = f'session:{session_id}'
    user_id = await self._redis.hget(session_key, "user_id")
    if not user_id: 
      return
    return await self.get_all_by_user_id(user_id=user_id)
  

  async def delete_by_id(self, session_id):
    session_key = f'session:{session_id}'
    user_id = await self._redis.hget(session_key, 'user_id')
    if not user_id:
      return
    user_sessions_key = f"user_sessions:{user_id}"
    async with self._redis.pipeline(transaction = True) as pipe:
      pipe.delete(session_key)
      pipe.srem(user_sessions_key, session_id)
      await pipe.execute()

  def next_id(self):
    return secrets.token_urlsafe(32)

