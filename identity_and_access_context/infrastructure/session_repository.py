import json
from identity_and_access_context.domain.session import Session

class RedisSessionRepository:
  def __init__(self, redis_client):
    self._redis = redis_client

  async def save(self, session: Session):
    await self._redis.hset(
      f'session:{session.session_id}', 
      mapping={
        'username': session.username, 
        'roles': json.dumps(session.roles)})

  async def get_by_id(self, session_id):
    data = await self._redis.hgetall(f'session:{session_id}')

    if not data:
      return None

    return Session(session_id=session_id, username=data['username'], roles=json.loads(data['roles']))

  async def delete(self, session_id):
    await self._redis.delete(f'session:{session_id}')

