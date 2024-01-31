"""buff/store/redis.py"""

from aiocache import Cache
from aiocache.serializers import JsonSerializer

from buff import SECRETS

aiocache_redis_config = {
    "cache": Cache.REDIS,
    "ttl": 60 * 60 * 24 * 7,
    "endpoint": SECRETS.REDIS_HOST,
    "port": SECRETS.REDIS_PORT,
    "password": SECRETS.REDIS_PASSWORD,
    "serializer": JsonSerializer(),
    "namespace": "openalex",
}
