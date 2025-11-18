from redis.asyncio import Redis

redis_cache = Redis(host="redis", port=6379)
