
from fastapi import FastAPI
from contextlib import asynccontextmanager
import subprocess
import sys
import os
import signal
from fastapi.middleware.cors import CORSMiddleware
from .api.routes import router as api_router
from .queue.redis_streams import init_stream

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_stream()
    
    # Start worker processes
    # Using the same python executable as the current process
    # Ensure PYTHONPATH is absolute path to src
    src_path = os.path.join(os.getcwd(), "src")
    
    num_workers = int(os.getenv("NUM_WORKERS", "2")) # Default to 2 workers
    workers = []
    
    print(f"Starting {num_workers} worker processes...")
    
    for i in range(num_workers):
        worker_process = subprocess.Popen(
            [sys.executable, "-u", "-m", "backend_pipeline.workers.worker"],
            cwd=os.getcwd(), # Ensure we are in project root
            env={**os.environ, "PYTHONPATH": src_path},
            stdout=sys.stdout,
            stderr=sys.stderr,
            bufsize=0
        )
        workers.append(worker_process)
        print(f"Started worker process {i+1} with PID: {worker_process.pid}")
    
    yield
    
    # Shutdown
    print("Shutting down worker processes...")
    for worker_process in workers:
        worker_process.terminate()
    
    for worker_process in workers:
        try:
            worker_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            worker_process.kill()
            
    print("All worker processes stopped.")

app = FastAPI(title="backend-pipeline OCR", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

@app.get("/health")
async def health():
    return {"status": "ok"}
