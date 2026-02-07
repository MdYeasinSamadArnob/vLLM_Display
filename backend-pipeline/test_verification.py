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

# Load env
env_path = r"g:\_era\vllm-ocr\backend\.env"
if os.path.exists(env_path):
    load_dotenv(env_path)
    print(f"Loaded env from {env_path}")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import pipeline
from backend_pipeline.workers.pipeline import process_job

async def test_run():
    # Mock save_result to avoid Redis dependency
    with patch('backend_pipeline.workers.pipeline.save_result') as mock_save:
        
        # Create a dummy job
        # We need a real image or a dummy image
        # Let's try to load the sample image
        image_path = r"g:\_era\vllm-ocr\backend\sample-images\nid-test.png"
        if not os.path.exists(image_path):
            print(f"Image not found at {image_path}, creating dummy")
            # Create dummy black image
            img = cv2.imencode('.jpg', 
                             cv2.rectangle(
                                 cv2.putText(
                                     255 * (lambda s: s)(import_numpy().zeros((500, 800, 3), dtype='uint8')), 
                                     "Dummy Name", (50, 50), 0, 1, (255, 255, 255), 2
                                 ), (0,0), (800,500), (0,0,0), -1
                             )[1]
            )[1].tobytes()
        else:
            with open(image_path, "rb") as f:
                img = f.read()

        job = {
            "job_id": "test_verification_001",
            "image_bytes": img,
            "mode": "schema",
            "schema": {
                "name": "Name",
                "name_bn": "Name (Bangla)",
                "dob": "Date of Birth",
                "nid_no": "NID No"
            }
        }

        print("Starting pipeline processing...")
        await process_job(job)
        
        # Check what was saved
        if mock_save.called:
            args, _ = mock_save.call_args
            job_id, result = args
            print("\n[Final Saved Result]")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print("save_result was not called!")

def import_numpy():
    import numpy
    return numpy

if __name__ == "__main__":
    asyncio.run(test_run())
