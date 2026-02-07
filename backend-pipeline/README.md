# Backend Pipeline

This directory contains the backend pipeline service for the VLLM OCR project.

## Prerequisites

- Python 3.10+
- Redis (External or Local)

## Setup

1.  **Check Location**:
    Look at your terminal prompt. It should end in `backend-pipeline`.
    
    *   If you are in `src\backend_pipeline`, run:
        ```powershell
        cd ..\..
        ```
    *   To be sure, run:
        ```powershell
        cd g:\_era\vllm-ocr\backend-pipeline
        ```

2.  **Create Virtual Environment** (if not exists):
    ```powershell
    py -m venv .venv
    ```

3.  **Activate Virtual Environment**:
    ```powershell
    .\.venv\Scripts\activate
    ```
    *If you see an error, ensure you ran step 2 and are in the correct folder.*

4.  **Install Dependencies**:
    
    ```powershell
    pip install -r requirements.txt
    ```

## Running the Backend (Local Development)

The backend is designed to run as a single process for local development. When you start the API server, it automatically launches the background worker process.

Run the following command:

```powershell
uvicorn backend_pipeline.main:app --app-dir src --host 0.0.0.0 --port 8001 --reload
```

*   **API Server**: `http://localhost:8001`
*   **Swagger UI**: `http://localhost:8001/docs`
*   **Worker**: Starts automatically in the background.

## Configuration

Ensure a `.env` file exists in `backend-pipeline` with necessary configuration.

Example `.env`:
```env
REDIS_URL=redis://default:password@10.11.200.99:6390
VLLM_URL=http://10.11.200.99:8090/
```
