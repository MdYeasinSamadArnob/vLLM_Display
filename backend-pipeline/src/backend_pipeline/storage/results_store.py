
import redis
import os
import json
from typing import Optional, Dict, Any

# Assuming same Redis as queue
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
r = redis.Redis.from_url(REDIS_URL)

def save_result(job_id: str, result: Dict[str, Any]):
    """
    Save job result to Redis.
    """
    try:
        # Use orjson if available for speed
        import orjson
        data = orjson.dumps(result)
    except ImportError:
        data = json.dumps(result).encode('utf-8')
        
    r.set(f"result:{job_id}", data)
    # Set expiry to 24 hours
    r.expire(f"result:{job_id}", 86400)

def get_result(job_id: str) -> Optional[Dict[str, Any]]:
    """
    Get job result from Redis.
    """
    data = r.get(f"result:{job_id}")
    if not data:
        return None
        
    try:
        import orjson
        return orjson.loads(data)
    except ImportError:
        return json.loads(data)
