#!/usr/bin/env python3
"""
Cache Service - Redis-based caching

Handles:
- LLM response caching
- Session storage
- Rate limiting
- Temporary data storage
"""

import json
from typing import Optional, Any
import redis.asyncio as redis
from loguru import logger
from config.environment import settings


class CacheService:
    """Redis-based cache service"""
    
    def __init__(self):
        self.redis_client = None
        self.ttl = settings.REDIS_TTL_SECONDS
        self.enabled = settings.CACHE_ENABLED
    
    async def initialize(self):
        """Initialize Redis connection"""
        if not self.enabled:
            logger.info("Cache service disabled")
            return
        
        try:
            self.redis_client = await redis.from_url(settings.REDIS_URL)
            await self.redis_client.ping()
            logger.info("✅ Cache service (Redis) initialized")
        except Exception as e:
            logger.error(f"Failed to initialize cache: {str(e)}")
            raise
    
    async def shutdown(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Cache service shutdown")
    
    async def health_check(self) -> bool:
        """Check if Redis is available"""
        if not self.enabled:
            return True
        
        try:
            if self.redis_client:
                await self.redis_client.ping()
                return True
            return False
        except Exception as e:
            logger.warning(f"Cache health check failed: {str(e)}")
            return False
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.enabled or not self.redis_client:
            return None
        
        try:
            value = await self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get failed: {str(e)}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache"""
        if not self.enabled or not self.redis_client:
            return
        
        try:
            ttl = ttl or self.ttl
            serialized = json.dumps(value)
            await self.redis_client.setex(key, ttl, serialized)
        except Exception as e:
            logger.error(f"Cache set failed: {str(e)}")
    
    async def delete(self, key: str):
        """Delete value from cache"""
        if not self.enabled or not self.redis_client:
            return
        
        try:
            await self.redis_client.delete(key)
        except Exception as e:
            logger.error(f"Cache delete failed: {str(e)}")
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        if not self.enabled or not self.redis_client:
            return False
        
        try:
            return await self.redis_client.exists(key) > 0
        except Exception as e:
            logger.error(f"Cache exists check failed: {str(e)}")
            return False
