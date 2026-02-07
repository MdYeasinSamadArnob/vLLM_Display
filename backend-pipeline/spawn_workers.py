import subprocess
import sys
import os
import time
from dotenv import load_dotenv

# Load env
env_path = r"g:\_era\vllm-ocr\backend\.env"
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    load_dotenv()

def main():
    src_path = os.path.join(os.getcwd(), "src")
    num_workers = int(os.getenv("NUM_WORKERS", "2"))
    workers = []
    
    print(f"--- Spawning {num_workers} Workers ---")
    
    try:
        for i in range(num_workers):
            worker_process = subprocess.Popen(
                [sys.executable, "-m", "backend_pipeline.workers.worker"],
                cwd=os.getcwd(),
                env={**os.environ, "PYTHONPATH": src_path}
            )
            workers.append(worker_process)
            print(f"Started worker {i+1} (PID: {worker_process.pid})")
            
        print(f"Workers running. Press Ctrl+C to stop.")
        
        while True:
            time.sleep(1)
            # Check if any worker died
            for i, w in enumerate(workers):
                if w.poll() is not None:
                    print(f"Worker {i+1} died! Restarting...")
                    # Restart logic could go here
                    
    except KeyboardInterrupt:
        print("\nStopping workers...")
        for w in workers:
            w.terminate()
        for w in workers:
            w.wait()
        print("Done.")

if __name__ == "__main__":
    main()
