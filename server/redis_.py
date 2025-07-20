from server.settings import Settings
import redis.asyncio as redis

settings = Settings()

redis_client = redis.from_url(
    settings.REDIS_URL,
    decode_responses=True
)