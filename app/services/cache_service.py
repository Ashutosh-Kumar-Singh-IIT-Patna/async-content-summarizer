import redis
from app.config import Config
import logging

logger = logging.getLogger(__name__)

redis_client = redis.Redis.from_url(Config.REDIS_URL)


def get_cached_summary(content_hash):
    try:
        result = redis_client.get(content_hash)
        if result:
            logger.info("Cache hit for hash: %s", content_hash)
        else:
            logger.info("Cache miss for hash: %s", content_hash)
        return result
    except Exception as e:
        logger.error("Cache get failed for hash %s: %s", content_hash, str(e))
        return None


def set_cached_summary(content_hash, summary):
    try:
        redis_client.set(content_hash, summary)
        logger.info("Cache set for hash: %s", content_hash)
    except Exception as e:
        logger.error("Cache set failed for hash %s: %s", content_hash, str(e))
