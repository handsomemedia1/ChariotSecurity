import redis
import json
from typing import Any, Optional
import logging
from shared.config.settings import settings

logger = logging.getLogger(__name__)

class RedisClient:
    def __init__(self, db: int = 0):
        self.client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=db,
            decode_responses=True
        )
        
    def get(self, key: str) -> Optional[Any]:
        '''Get value from Redis'''
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f'Redis GET error: {str(e)}')
            return None
    
    def set(self, key: str, value: Any, expire: int = None) -> bool:
        '''Set value in Redis'''
        try:
            json_value = json.dumps(value)
            if expire:
                return self.client.setex(key, expire, json_value)
            return self.client.set(key, json_value)
        except Exception as e:
            logger.error(f'Redis SET error: {str(e)}')
            return False
    
    def delete(self, key: str) -> bool:
        '''Delete key from Redis'''
        try:
            return bool(self.client.delete(key))
        except Exception as e:
            logger.error(f'Redis DELETE error: {str(e)}')
            return False
    
    def exists(self, key: str) -> bool:
        '''Check if key exists'''
        try:
            return bool(self.client.exists(key))
        except Exception as e:
            logger.error(f'Redis EXISTS error: {str(e)}')
            return False
    
    def incr(self, key: str) -> int:
        '''Increment value'''
        try:
            return self.client.incr(key)
        except Exception as e:
            logger.error(f'Redis INCR error: {str(e)}')
            return 0
    
    def expire(self, key: str, seconds: int) -> bool:
        '''Set expiration on key'''
        try:
            return bool(self.client.expire(key, seconds))
        except Exception as e:
            logger.error(f'Redis EXPIRE error: {str(e)}')
            return False

# Initialize Redis clients
redis_cache = RedisClient(db=settings.REDIS_CACHE_DB)
redis_queue = RedisClient(db=settings.REDIS_QUEUE_DB)
redis_session = RedisClient(db=settings.REDIS_DB)
