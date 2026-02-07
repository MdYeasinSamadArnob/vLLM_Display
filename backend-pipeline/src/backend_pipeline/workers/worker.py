
import asyncio
import json
import logging
import os
from dotenv import load_dotenv

# Load env before imports that rely on it
env_path = r"g:\_era\vllm-ocr\backend\.env"
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    load_dotenv()

from ..queue.redis_streams import r, STREAM, GROUP, init_stream
from .pipeline import process_job

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("worker")

import uuid

WORKER_NAME = f"worker-{uuid.uuid4().hex[:8]}"

async def worker_loop():
    logger.info(f"Starting worker {WORKER_NAME}...")
    init_stream()
    
    while True:
        try:
            # Read from stream
            entries = r.xreadgroup(
                GROUP, WORKER_NAME,
                {STREAM: ">"},
                count=1,
                block=5000
            )

            if not entries:
                await asyncio.sleep(0.1)
                continue

            for stream, messages in entries:
                for msg_id, msg in messages:
                    try:
                        job_data = msg.get(b"data")
                        if not job_data:
                            logger.warning(f"Empty data in message {msg_id}")
                            r.xack(STREAM, GROUP, msg_id)
                            continue
                            
                        # Handle orjson/json
                        try:
                            import orjson
                            job = orjson.loads(job_data)
                        except ImportError:
                            job = json.loads(job_data)
                        except Exception as e:
                            logger.error(f"Failed to decode job data: {e}")
                            r.xack(STREAM, GROUP, msg_id) # Ack bad data to skip it
                            continue

                        logger.info(f"Received job {job.get('job_id')}")
                        await process_job(job)
                        
                        # Acknowledge
                        r.xack(STREAM, GROUP, msg_id)
                        
                    except Exception as e:
                        logger.error(f"Error processing message {msg_id}: {e}", exc_info=True)
                        # Move to DLQ
                        r.xadd("ocr_dlq", {"error": str(e), "original_msg": job_data})
                        r.xack(STREAM, GROUP, msg_id) # Ack so we don't loop forever on it
                        
        except Exception as e:
            logger.error(f"Worker loop error: {e}")
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(worker_loop())
