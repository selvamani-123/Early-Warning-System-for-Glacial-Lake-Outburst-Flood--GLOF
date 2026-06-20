# pyrefly: ignore [missing-import]
import redis.asyncio as redis
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Create connection pool
redis_pool = redis.ConnectionPool.from_url(REDIS_URL)

def get_redis():
    return redis.Redis(connection_pool=redis_pool)
