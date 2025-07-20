import redis.asyncio as redis

from server.settings import Settings

settings = Settings()

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
