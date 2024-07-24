import redis.asyncio as aioredis


async def get_redis_connection(redis_url):
    return aioredis.from_url(redis_url)


async def set_key(redis, key, value):
    await redis.set(key, value)


async def get_key(redis, key):
    return await redis.get(key)


async def delete_key(redis, key):
    await redis.delete(key)
