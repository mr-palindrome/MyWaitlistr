from redis.asyncio import Redis, BlockingConnectionPool
from src.config.settings import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD

class RedisManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._redis = None
        return cls._instance

    def __init__(self):
        if self._redis:
            return

        self._redis = Redis(
            connection_pool=BlockingConnectionPool(
                host=REDIS_HOST,
                port=REDIS_PORT,
                password=REDIS_PASSWORD,
                db=0,
                decode_responses=True,
            )
        )

    async def get_redis(self):
        return self._redis

    async def close(self):
        await self._redis.close()

redis_manager = RedisManager()

async def get_redis():
    return await redis_manager.get_redis()