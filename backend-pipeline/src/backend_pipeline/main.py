
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
    
    # Start the worker process
    # Using the same python executable as the current process
    # Ensure PYTHONPATH is absolute path to src
    src_path = os.path.join(os.getcwd(), "src")
    worker_process = subprocess.Popen(
        [sys.executable, "-m", "backend_pipeline.workers.worker"],
        cwd=os.getcwd(), # Ensure we are in project root
        env={**os.environ, "PYTHONPATH": src_path}
    )
    print(f"Started worker process with PID: {worker_process.pid} (PYTHONPATH={src_path})")
    
    yield
    
    # Shutdown
    print("Shutting down worker process...")
    worker_process.terminate()
    try:
        worker_process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        worker_process.kill()
    print("Worker process stopped.")

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
