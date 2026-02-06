
import redis
import os
import json
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
r = redis.Redis.from_url(REDIS_URL)

STREAM = "ocr_jobs"
GROUP = "ocr_workers"
DLQ = "ocr_dlq"

def init_stream():
    """Initialize the stream and consumer group if they don't exist."""
    try:
        # Create consumer group (and stream if it doesn't exist)
        r.xgroup_create(STREAM, GROUP, id="0", mkstream=True)
        logger.info(f"Initialized stream '{STREAM}' and group '{GROUP}'")
    except redis.exceptions.ResponseError as e:
        if "BUSYGROUP Consumer Group name already exists" in str(e):
            logger.info(f"Group '{GROUP}' already exists.")
        else:
            logger.error(f"Error initializing stream: {e}")

async def enqueue_job(job: dict):
    """Add a job to the Redis Stream."""
    # Ensure job is JSON serializable
    # For binary data (like images), we might want to store in S3/MinIO and pass reference
    # But for MVP with Redis Streams, we can pass small payloads.
    # If image_bytes is in job, we assume it's base64 encoded string or similar before calling this
    # Or we handle serialization here.
    
    # Using orjson for speed if available, else json
    try:
        import orjson
        data = orjson.dumps(job)
    except ImportError:
        data = json.dumps(job).encode('utf-8')
        
    r.xadd(STREAM, {"data": data})
    logger.info(f"Enqueued job: {job.get('job_id')}")
