# app/invalidate_cache.py
from functools import wraps
from app import redis_client

def invalidate_cache(pattern="cache:*"):
    """
    Decorator to invalidate Redis cache matching the given pattern.
    Use pattern to target cached GET routes (e.g., 'cache:*api/users*').
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)  # Execute the route function
            try:
                # Get all keys matching the pattern
                keys = redis_client.keys(pattern)
                if keys:
                    redis_client.delete(*keys)
                    print(f"🗑 Cleared {len(keys)} cache keys matching '{pattern}'")
                    print(f"Cleared keys: {keys}")  # verbose log to see actual keys
                else:
                    print(f"⚠️ No cache keys matched the pattern '{pattern}'")
            except Exception as e:
                print("Cache invalidation error:", e)
            return result
        return wrapper
    return decorator