import asyncio
import httpx
import time
import os
import json
from datetime import datetime

API_URL = "http://localhost:8001"
IMAGE_PATH = r"g:\_era\vllm-ocr\backend\sample-images\nid-test.png"

async def main():
    if not os.path.exists(IMAGE_PATH):
        print(f"Error: Image not found at {IMAGE_PATH}")
        return

    with open(IMAGE_PATH, "rb") as f:
        image_bytes = f.read()

    print(f"--- Running Full Pipeline Test (Scribe + Judge) ---")
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        # Submit with SCHEMA to trigger Judge
        files = {"file": ("nid-test.png", image_bytes, "image/png")}
        data = {"schema": json.dumps({"name": "Name", "nid_no": "NID Number"})}
        
        start_time = time.time()
        response = await client.post(f"{API_URL}/v1/ocr/schema", files=files, data=data)
        response.raise_for_status()
        job_id = response.json()["job_id"]
        print(f"Job submitted: {job_id}")
        
        # Poll
        while True:
            res = await client.get(f"{API_URL}/v1/ocr/results/{job_id}")
            status = res.json().get("status")
            if status == "completed":
                duration = time.time() - start_time
                print(f"✅ Job COMPLETED in {duration:.2f}s")
                print("Result:", json.dumps(res.json().get("result"), indent=2))
                break
            elif status == "failed":
                print("❌ Job FAILED")
                break
            await asyncio.sleep(0.5)

if __name__ == "__main__":
    asyncio.run(main())
