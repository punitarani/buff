"""buff/openalex/config.py"""

from aiocache import Cache
from aiocache.serializers import JsonSerializer

from config import REDIS_HOST, REDIS_PASSWORD, REDIS_PORT

aiocache_redis_config = {
    "cache": Cache.REDIS,
    "ttl": 60 * 60 * 24 * 7,
    "endpoint": REDIS_HOST,
    "port": REDIS_PORT,
    "password": REDIS_PASSWORD,
    "serializer": JsonSerializer(),
    "namespace": "openalex",
}
