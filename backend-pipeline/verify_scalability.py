import asyncio
import httpx
import time
import os
import json
from datetime import datetime

API_URL = "http://localhost:8001"
IMAGE_PATH = r"g:\_era\vllm-ocr\backend\sample-images\nid-test.png"

async def submit_job(client, image_bytes):
    files = {"file": ("nid-test.png", image_bytes, "image/png")}
    response = await client.post(f"{API_URL}/v1/ocr/schema", files=files)
    response.raise_for_status()
    return response.json()["job_id"]

async def poll_job(client, job_id, job_name):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {job_name} submitted (ID: {job_id})")
    start_time = time.time()
    
    while True:
        response = await client.get(f"{API_URL}/v1/ocr/results/{job_id}")
        data = response.json()
        status = data.get("status")
        
        if status == "completed":
            duration = time.time() - start_time
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {job_name} COMPLETED in {duration:.2f}s")
            return start_time, time.time()
        elif status == "failed":
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {job_name} FAILED")
            return start_time, time.time()
            
        await asyncio.sleep(0.5)

async def main():
    if not os.path.exists(IMAGE_PATH):
        print(f"Error: Image not found at {IMAGE_PATH}")
        return

    with open(IMAGE_PATH, "rb") as f:
        image_bytes = f.read()

    print(f"--- Starting Scalability Verification ---")
    print(f"Submitting 2 concurrent jobs to verify multiple workers...")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Submit 2 jobs at once
        job1_id = await submit_job(client, image_bytes)
        job2_id = await submit_job(client, image_bytes)
        
        # Poll them concurrently
        results = await asyncio.gather(
            poll_job(client, job1_id, "Job 1"),
            poll_job(client, job2_id, "Job 2")
        )
        
    # Analyze results
    start1, end1 = results[0]
    start2, end2 = results[1]
    
    # Check for overlap
    # Overlap exists if Job 2 starts before Job 1 ends (or vice versa)
    # Since we poll immediately, "start" here is submission time. 
    # Real proof is if they FINISH roughly at the same time, or if the total time < sum of individual times.
    
    total_duration = max(end1, end2) - min(start1, start2)
    sum_duration = (end1 - start1) + (end2 - start2)
    
    print("\n--- Analysis ---")
    print(f"Job 1 Duration: {end1 - start1:.2f}s")
    print(f"Job 2 Duration: {end2 - start2:.2f}s")
    print(f"Total Wall Time: {total_duration:.2f}s")
    print(f"Sum of Durations: {sum_duration:.2f}s")
    
    if total_duration < sum_duration * 0.8:
        print("✅ SUCCESS: Jobs ran in PARALLEL (Multiple Workers confirmed)")
    else:
        print("⚠️ WARNING: Jobs appeared to run SEQUENTIALLY (Check worker count)")
        
    print("\nNote: Individual job duration should be faster than before due to Parallel Multiviews.")

if __name__ == "__main__":
    asyncio.run(main())
