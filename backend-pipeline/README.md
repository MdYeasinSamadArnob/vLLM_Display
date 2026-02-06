# Backend Pipeline

This directory contains the backend pipeline service for the VLLM OCR project.

## Prerequisites

- Python 3.10+
- Redis (External or Local)

## Setup

1.  **Create a Virtual Environment**:
    
    From the project root (`G:\_era\vllm-ocr`):
    ```powershell
    py -m venv backend-pipeline\.venv
    ```

2.  **Activate Virtual Environment**:
    
    ```powershell
    backend-pipeline\.venv\Scripts\activate
    ```

3.  **Install Dependencies**:
    
    ```powershell
    pip install fastapi uvicorn[standard] pydantic redis httpx opencv-python-headless numpy pillow orjson python-dotenv tenacity prometheus-client
    ```

## Running the Services

You need to run two separate processes: the API server and the Worker.

### 1. API Server

Starts the FastAPI server on port 8001.

```powershell
# From project root
backend-pipeline\.venv\Scripts\python -m uvicorn backend_pipeline.main:app --host 0.0.0.0 --port 8001 --reload --app-dir backend-pipeline/src
```

### 2. Worker

Starts the background worker that processes OCR jobs from Redis.

```powershell
# From project root
set PYTHONPATH=backend-pipeline/src
backend-pipeline\.venv\Scripts\python -m backend_pipeline.workers.worker
```

## Configuration

Check `.env` for configuration settings (Redis URL, etc.).
