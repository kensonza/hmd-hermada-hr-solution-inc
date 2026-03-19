# app/cache_response.py
import functools
import json
from flask import request
from app import redis_client

def cache_response(timeout=60):
    """
    Decorator to cache GET route responses in Redis.
    Uses literal request.path + query params as cache key so that
    @invalidate_cache can properly clear cached keys.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Unique cache key based on URL path + query params
                cache_key = f"cache:{request.path}"
                if request.args:
                    cache_key += "?" + "&".join([f"{k}={v}" for k,v in request.args.items()])

                # Check cache
                cached = redis_client.get(cache_key)
                if cached:
                    print(f"🔥 Cache HIT for key: {cache_key}")
                    return json.loads(cached)

                print(f"✨ Cache MISS for key: {cache_key}")

                # Execute the route function
                response = func(*args, **kwargs)

                # Save response to cache
                redis_client.set(cache_key, json.dumps(response), ex=timeout)

                return response

            except Exception as e:
                print("Cache error:", e)
                return func(*args, **kwargs)

        return wrapper
    return decorator