import functools
import json
from flask import request, session
from app import redis_client

def cache_response(timeout=60):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # 🔐 Identify user
                user_id = session.get("token_id", "anonymous")

                # Unique cache key per user
                cache_key = f"cache:{user_id}:{request.path}"

                # Include query params
                if request.args:
                    cache_key += "?" + "&".join(
                        [f"{k}={v}" for k, v in request.args.items()]
                    )

                # Check cache
                cached = redis_client.get(cache_key)
                if cached:
                    print(f"🔥 Cache HIT for key: {cache_key}")
                    return json.loads(cached)

                print(f"✨ Cache MISS for key: {cache_key}")

                # Execute function
                response = func(*args, **kwargs)

                # Save to cache
                redis_client.set(cache_key, json.dumps(response), ex=timeout)

                return response

            except Exception as e:
                print("Cache error:", e)
                return func(*args, **kwargs)

        return wrapper
    return decorator