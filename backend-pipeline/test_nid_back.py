
import asyncio
import logging
import os
import sys
import json
import cv2
from dotenv import load_dotenv
from unittest.mock import MagicMock, patch

# Setup paths
base_dir = os.getcwd()
if os.path.basename(base_dir) != "backend-pipeline":
    src_path = os.path.join(base_dir, "backend-pipeline", "src")
else:
    src_path = os.path.join(base_dir, "src")

sys.path.append(src_path)

# Load env from backend if available
env_path = r"g:\_era\vllm-ocr\backend\.env"
if os.path.exists(env_path):
    load_dotenv(env_path)
    print(f"Loaded env from {env_path}")

# Explicitly set URLs if not in env, to match project memory
if not os.getenv("VLLM_URL"):
    os.environ["VLLM_URL"] = "http://10.11.200.99:8090/"
if not os.getenv("OLLAMA_BASE_URL"):
    os.environ["OLLAMA_BASE_URL"] = "http://10.11.200.99:11434"

print(f"VLLM_URL: {os.environ.get('VLLM_URL')}")
print(f"OLLAMA_BASE_URL: {os.environ.get('OLLAMA_BASE_URL')}")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import pipeline
from backend_pipeline.workers.pipeline import process_job

async def test_run():
    # Mock save_result to avoid Redis dependency
    with patch('backend_pipeline.workers.pipeline.save_result') as mock_save:
        
        image_path = r"g:\_era\vllm-ocr\backend\sample-images\7135447_b.png"
        if not os.path.exists(image_path):
            print(f"Error: Image not found at {image_path}")
            return

        with open(image_path, "rb") as f:
            img_bytes = f.read()

        # NID Back Schema
        schema = {
            "address_bn": "Address in Bangla (Thikana)",
            "blood_group": "Blood Group",
            "place_of_birth": "Place of Birth",
            "issue_date": "Issue Date",
            "mrz_line1": "MRZ Line 1",
            "mrz_line2": "MRZ Line 2",
            "mrz_line3": "MRZ Line 3"
        }

        job = {
            "job_id": "test_nid_back_001",
            "image_bytes": img_bytes,
            "mode": "schema",
            "schema": schema
        }

        print("Starting pipeline processing for NID Back...")
        await process_job(job)
        
        # Check what was saved
        if mock_save.called:
            args, _ = mock_save.call_args
            job_id, result = args
            print("\n[Final Saved Result]")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print("save_result was not called!")

if __name__ == "__main__":
    asyncio.run(test_run())
