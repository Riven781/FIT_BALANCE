from config import REDIS_HOST, REDIS_PORT
import redis.asyncio as redis

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def get_redis():
  return redis_client