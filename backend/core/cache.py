"""
Redis caching layer for performance optimization
"""
import json
import hashlib
from typing import Optional, Any, Callable
from functools import wraps
import redis
from datetime import timedelta

from core.config import settings


class CacheManager:
    """Redis cache manager with automatic serialization"""
    
    def __init__(self):
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=5
            )
            self.redis_client.ping()
            self.enabled = True
        except Exception as e:
            print(f"Redis not available: {e}. Caching disabled.")
            self.redis_client = None
            self.enabled = False
    
    def _make_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        key_data = f"{prefix}:{args}:{sorted(kwargs.items())}"
        key_hash = hashlib.md5(key_data.encode()).hexdigest()
        return f"cache:{prefix}:{key_hash}"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.enabled:
            return None
        
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            print(f"Cache get error: {e}")
        
        return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL (seconds)"""
        if not self.enabled:
            return False
        
        try:
            serialized = json.dumps(value, default=str)
            self.redis_client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.enabled:
            return False
        
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        if not self.enabled:
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
        except Exception as e:
            print(f"Cache clear error: {e}")
        
        return 0
    
    def invalidate_query(self, query_id: int):
        """Invalidate all cache entries for a query"""
        self.clear_pattern(f"cache:query:{query_id}:*")
        self.clear_pattern(f"cache:report:*:query:{query_id}:*")


# Global cache instance
cache = CacheManager()


def cached(prefix: str, ttl: int = 3600):
    """
    Decorator for caching function results
    
    Usage:
        @cached("agent_result", ttl=1800)
        def expensive_function(arg1, arg2):
            return result
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = cache._make_key(prefix, *args, **kwargs)
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Store in cache
            cache.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


def invalidate_cache(prefix: str, *args, **kwargs):
    """Invalidate specific cache entry"""
    cache_key = cache._make_key(prefix, *args, **kwargs)
    cache.delete(cache_key)


# Cache statistics
class CacheStats:
    """Track cache performance"""
    
    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.sets = 0
        self.deletes = 0
    
    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return (self.hits / total * 100) if total > 0 else 0
    
    def reset(self):
        self.hits = 0
        self.misses = 0
        self.sets = 0
        self.deletes = 0
    
    def to_dict(self):
        return {
            "hits": self.hits,
            "misses": self.misses,
            "sets": self.sets,
            "deletes": self.deletes,
            "hit_rate": round(self.hit_rate, 2),
            "total_requests": self.hits + self.misses
        }


cache_stats = CacheStats()


# Cached query functions
@cached("query_status", ttl=30)
def get_cached_query_status(query_id: int):
    """Cache query status for 30 seconds"""
    from services.query_service import QueryService
    from core.database import SessionLocal
    
    db = SessionLocal()
    try:
        service = QueryService(db)
        return service.get_query_status(query_id)
    finally:
        db.close()


@cached("query_result", ttl=3600)
def get_cached_query_result(query_id: int):
    """Cache completed query results for 1 hour"""
    from services.query_service import QueryService
    from core.database import SessionLocal
    
    db = SessionLocal()
    try:
        service = QueryService(db)
        return service.get_analysis_result(query_id)
    finally:
        db.close()


@cached("report_detail", ttl=3600)
def get_cached_report(report_id: int):
    """Cache report details for 1 hour"""
    from services.report_service import ReportService
    from core.database import SessionLocal
    
    db = SessionLocal()
    try:
        service = ReportService(db)
        return service.get_report_detail(report_id)
    finally:
        db.close()


@cached("system_status", ttl=60)
def get_cached_system_status():
    """Cache system status for 1 minute"""
    from services.agent_service import AgentService
    from core.database import SessionLocal
    
    db = SessionLocal()
    try:
        service = AgentService(db)
        import asyncio
        loop = asyncio.new_event_loop()
        result = loop.run_until_complete(service.get_system_status())
        loop.close()
        return result
    finally:
        db.close()
