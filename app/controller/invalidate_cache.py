from functools import wraps
from app import redis_client

def invalidate_cache(pattern="cache:*"):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            try:
                keys_to_delete = []

                # Use SCAN (safe for production)
                for key in redis_client.scan_iter(pattern):
                    keys_to_delete.append(key)

                if keys_to_delete:
                    redis_client.delete(*keys_to_delete)
                    print(f"🗑 Cleared {len(keys_to_delete)} cache keys matching '{pattern}'")
                else:
                    print(f"⚠️ No cache keys matched '{pattern}'")

            except Exception as e:
                print("Cache invalidation error:", e)

            return result
        return wrapper
    return decorator