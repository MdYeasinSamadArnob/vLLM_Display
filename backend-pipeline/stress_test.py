import asyncio
import httpx
import time
import os
import sys
from datetime import datetime

API_URL = "http://localhost:8001"
IMAGE_PATH = r"g:\_era\vllm-ocr\backend\sample-images\nid-test.png"
NUM_JOBS = 10

async def submit_job(client, image_bytes, i):
    files = {"file": ("nid-test.png", image_bytes, "image/png")}
    try:
        response = await client.post(f"{API_URL}/v1/ocr/schema", files=files)
        response.raise_for_status()
        job_id = response.json()["job_id"]
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Job {i+1} submitted (ID: {job_id})")
        return job_id
    except Exception as e:
        print(f"Failed to submit job {i+1}: {e}")
        return None

async def poll_job(client, job_id, job_name):
    start_time = time.time()
    while True:
        try:
            response = await client.get(f"{API_URL}/v1/ocr/results/{job_id}")
            if response.status_code != 200:
                await asyncio.sleep(0.5)
                continue
                
            data = response.json()
            status = data.get("status")
            
            if status == "completed":
                duration = time.time() - start_time
                print(f"[{datetime.now().strftime('%H:%M:%S')}] {job_name} COMPLETED in {duration:.2f}s")
                return duration
            elif status == "failed":
                print(f"[{datetime.now().strftime('%H:%M:%S')}] {job_name} FAILED")
                return None
                
            await asyncio.sleep(0.5)
        except Exception as e:
            print(f"Error polling {job_name}: {e}")
            await asyncio.sleep(1)

async def main():
    if not os.path.exists(IMAGE_PATH):
        print(f"Error: Image not found at {IMAGE_PATH}")
        return

    with open(IMAGE_PATH, "rb") as f:
        image_bytes = f.read()

    print(f"--- Starting Stress Test ---")
    print(f"Submitting {NUM_JOBS} concurrent jobs to measure throughput...")
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        # Submit all jobs rapidly
        start_time = time.time()
        job_tasks = [submit_job(client, image_bytes, i) for i in range(NUM_JOBS)]
        job_ids = await asyncio.gather(*job_tasks)
        
        valid_job_ids = [(i, jid) for i, jid in enumerate(job_ids) if jid]
        
        if not valid_job_ids:
            print("No jobs submitted successfully.")
            return

        # Poll all jobs
        poll_tasks = [poll_job(client, jid, f"Job {i+1}") for i, jid in valid_job_ids]
        durations = await asyncio.gather(*poll_tasks)
        
        end_time = time.time()
        total_time = end_time - start_time
        successful_jobs = len([d for d in durations if d is not None])
        
        print("\n--- Stress Test Results ---")
        print(f"Total Jobs: {NUM_JOBS}")
        print(f"Successful: {successful_jobs}")
        print(f"Total Wall Time: {total_time:.2f}s")
        
        if successful_jobs > 0:
            avg_latency = sum([d for d in durations if d is not None]) / successful_jobs
            throughput_rpm = (successful_jobs / total_time) * 60
            print(f"Average Latency per Job: {avg_latency:.2f}s")
            print(f"Throughput: {throughput_rpm:.1f} jobs/minute")
            
            # Estimate Capacity
            print("\n--- Capacity Estimation ---")
            print(f"With current workers (likely 2): ~{throughput_rpm:.1f} jobs/minute")
            print(f"Projected with 10 workers: ~{throughput_rpm * 5:.1f} jobs/minute (assuming VRAM allows)")

if __name__ == "__main__":
    asyncio.run(main())
