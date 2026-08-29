import json
from identity_and_access_context.domain.role import Role

class RedisUserRolesCache:
  def __init__(self, redis):
    self._redis = redis

  async def set(self, user_id, roles: list[Role], ttl=60 * 60 * 24):
    user_roles_key = f'user_roles:{user_id}'
    async with self._redis.pipeline(transaction=True) as pipe:
      pipe.hset(
        user_roles_key,
        mapping = {
          'roles' : json.dumps(list(roles))
        }
      )
      pipe.expire(user_roles_key, ttl,  gt=True)
      await pipe.execute()

  async def get(self, user_id) -> list[Role] | None:
    user_roles_key = f'user_roles:{user_id}'
    roles = await self._redis.hget(user_roles_key, "roles")
    if roles is None:
      return None
    return json.loads(roles)
  
  async def invalidate(self, user_id):
    user_roles_key = f'user_roles:{user_id}'
    await self._redis.delete(user_roles_key)