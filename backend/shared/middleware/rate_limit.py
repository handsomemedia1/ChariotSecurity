from fastapi import HTTPException, Request
from typing import Callable
import time
from shared.utils.redis_client import redis_cache
from shared.config.settings import settings

class RateLimiter:
    def __init__(self, calls: int, period: int):
        self.calls = calls
        self.period = period
    
    async def __call__(self, request: Request, call_next: Callable):
        # Get client identifier (IP or user ID)
        client_ip = request.client.host
        key = f'rate_limit:{client_ip}:{request.url.path}'
        
        # Get current count
        current = redis_cache.get(key)
        if current is None:
            redis_cache.set(key, 1, self.period)
            return await call_next(request)
        
        if int(current) >= self.calls:
            raise HTTPException(
                status_code=429,
                detail=f'Rate limit exceeded. Try again in {self.period} seconds'
            )
        
        redis_cache.incr(key)
        return await call_next(request)

# Rate limiters for different endpoints
standard_rate_limit = RateLimiter(calls=60, period=60)  # 60 per minute
strict_rate_limit = RateLimiter(calls=10, period=60)  # 10 per minute
