"""Redis caching utilities"""
import redis
import json
import logging
from functools import wraps
from typing import Optional, Callable, Any
from app.config import settings

logger = logging.getLogger(__name__)

# Redis client instance
redis_client: Optional[redis.Redis] = None


def get_redis_client() -> redis.Redis:
    """
    Get or create Redis client.

    Returns:
        redis.Redis: Redis client instance
    """
    global redis_client

    if redis_client is None:
        try:
            redis_client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Test connection
            redis_client.ping()
            logger.info(f"Connected to Redis at {settings.REDIS_URL}")
        except redis.ConnectionError as e:
            logger.warning(f"Could not connect to Redis: {e}. Caching disabled.")
            redis_client = None
        except Exception as e:
            logger.error(f"Unexpected error connecting to Redis: {e}")
            redis_client = None

    return redis_client


def cache_result(key_prefix: str, ttl: int = 300):
    """
    Decorator to cache function results in Redis.

    Args:
        key_prefix: Prefix for cache key
        ttl: Time to live in seconds (default: 5 minutes)

    Usage:
        @cache_result("user_info", ttl=300)
        def get_user_info(user_id: int):
            # expensive operation
            return user_data

    Cache key format: {key_prefix}:{arg1}:{arg2}:...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            client = get_redis_client()

            # If Redis not available, bypass cache
            if client is None:
                return func(*args, **kwargs)

            # Generate cache key from function arguments
            cache_key = f"{key_prefix}:"
            if args:
                cache_key += ":".join(str(arg) for arg in args)
            if kwargs:
                cache_key += ":" + ":".join(f"{k}={v}" for k, v in sorted(kwargs.items()))

            try:
                # Try to get from cache
                cached = client.get(cache_key)
                if cached:
                    logger.debug(f"Cache HIT: {cache_key}")
                    return json.loads(cached)

                # Cache miss - execute function
                logger.debug(f"Cache MISS: {cache_key}")
                result = func(*args, **kwargs)

                # Store in cache
                client.setex(cache_key, ttl, json.dumps(result, default=str))
                return result

            except redis.RedisError as e:
                logger.warning(f"Redis error, bypassing cache: {e}")
                return func(*args, **kwargs)
            except Exception as e:
                logger.exception(f"Unexpected caching error: {e}")
                return func(*args, **kwargs)

        return wrapper
    return decorator


def invalidate_cache(pattern: str):
    """
    Invalidate cache entries matching pattern.

    Args:
        pattern: Redis key pattern (e.g., "user_info:123:*")

    Example:
        invalidate_cache("user_info:123:*")  # Clear all user 123 cache
        invalidate_cache("metrics_summary:*")  # Clear all metrics summaries
    """
    client = get_redis_client()

    if client is None:
        return

    try:
        keys = client.keys(pattern)
        if keys:
            client.delete(*keys)
            logger.info(f"Invalidated {len(keys)} cache entries matching '{pattern}'")
    except redis.RedisError as e:
        logger.warning(f"Failed to invalidate cache: {e}")


def clear_all_cache():
    """Clear entire cache (use with caution!)"""
    client = get_redis_client()

    if client is None:
        return

    try:
        client.flushdb()
        logger.warning("Cleared entire Redis cache")
    except redis.RedisError as e:
        logger.error(f"Failed to clear cache: {e}")


class CacheManager:
    """Context manager for temporary cache bypass"""

    def __init__(self):
        self.original_client = None

    def __enter__(self):
        """Disable cache temporarily"""
        global redis_client
        self.original_client = redis_client
        redis_client = None
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Re-enable cache"""
        global redis_client
        redis_client = self.original_client


# Cache statistics
def get_cache_stats() -> dict:
    """
    Get Redis cache statistics.

    Returns:
        dict: Cache statistics (keys, memory, hits, misses, etc.)
    """
    client = get_redis_client()

    if client is None:
        return {"status": "unavailable", "keys": 0, "hits": 0, "misses": 0, "hit_rate": 0.0}

    try:
        info = client.info("stats")
        keyspace = client.info("keyspace")

        return {
            "status": "connected",
            "keys": keyspace.get("db0", {}).get("keys", 0),
            "hits": info.get("keyspace_hits", 0),
            "misses": info.get("keyspace_misses", 0),
            "hit_rate": _calculate_hit_rate(
                info.get("keyspace_hits", 0),
                info.get("keyspace_misses", 0)
            )
        }
    except Exception as e:
        logger.error(f"Failed to get cache stats: {e}")
        return {"status": "error", "message": str(e)}


def _calculate_hit_rate(hits: int, misses: int) -> float:
    """Calculate cache hit rate percentage"""
    total = hits + misses
    if total == 0:
        return 0.0
    return round((hits / total) * 100, 2)
