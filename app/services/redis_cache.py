import aioredis
import os
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")
if not REDIS_URL:
    raise ValueError("REDIS_URL not found in .env")
redis = aioredis.from_url(REDIS_URL, decode_responses=True)


async def set_cache(key: str, value: str, expire: int = 60):
    await redis.set(key, value, ex=expire)

async def get_cache(key: str):
    return await redis.get(key)
