import time
import redis

class RateLimiter:
    def __init__(self, redis_host: str = 'localhost', redis_port: int = 6379):
        self.r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)

    def is_allowed(self, domain: str, max_requests: int = 10, window_seconds: int = 60) -> bool:
        key = f"rate_limit:{domain}"
        current_time = int(time.time())
        pipeline = self.r.pipeline()
        
        pipeline.zremrangebyscore(key, 0, current_time - window_seconds)
        pipeline.zcard(key)
        pipeline.zadd(key, {str(current_time): current_time})
        pipeline.expire(key, window_seconds)
        
        results = pipeline.execute()
        request_count = results[1]
        
        return request_count < max_requests

    def wait_if_needed(self, domain: str, max_requests: int = 10, window_seconds: int = 60):
        while not self.is_allowed(domain, max_requests, window_seconds):
            time.sleep(0.5)