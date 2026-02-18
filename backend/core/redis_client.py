"""
Redis client for caching and session management
"""

import redis.asyncio as redis
from backend.core.config import settings
from typing import Optional


class RedisClient:
    def __init__(self):
        self.client: Optional[redis.Redis] = None
    
    async def connect(self):
        """Connect to Redis"""
        self.client = await redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.client:
            await self.client.close()
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from Redis"""
        if self.client:
            return await self.client.get(key)
        return None
    
    async def set(self, key: str, value: str, ex: Optional[int] = None):
        """Set value in Redis"""
        if self.client:
            await self.client.set(key, value, ex=ex)
    
    async def delete(self, key: str):
        """Delete key from Redis"""
        if self.client:
            await self.client.delete(key)
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        if self.client:
            return await self.client.exists(key) > 0
        return False


redis_client = RedisClient()
