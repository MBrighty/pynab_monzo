from redis import Redis
import os

_redis = None


def get_redis():
    global _redis
    if _redis is None:
        REDIS_URL = os.environ.get("REDIS_URL")
        _redis = Redis.from_url(REDIS_URL)
    return _redis


def set_redis(redis):
    global _redis
    _redis = redis
