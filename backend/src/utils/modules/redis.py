from redis.asyncio import Redis

redis_client: Redis | None = None


async def init_redis() -> None:
    global redis_client
    redis_client = Redis.from_url(url="redis://redis:6379/0", encoding="utf-8", decode_responses=True)


async def close_redis() -> None:
    global redis_client
    if redis_client:
        await redis_client.aclose()


async def get_redis() -> Redis | None:
    return redis_client
