import redis
from django.conf import settings

redis_password = getattr(settings, "REDIS_PASSWORD", None)

redis_client = redis.StrictRedis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=redis_password or None,
    decode_responses=True,
)
