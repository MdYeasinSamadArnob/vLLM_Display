# VLLM-OCR Pro

A high-performance, modular OCR application using state-of-the-art Vision-Language Models (VLM).

## Features

- **Modern UI**: Built with Next.js, Tailwind CSS, and Framer Motion.
- **Advanced OCR**: Uses Ollama (DeepSeek-OCR, Qwen3-VL) for high-accuracy text extraction.
- **Interactive Scanning**: Visual scanning effects with polygon identification.
- **Multi-Format Output**: View results as Plain Text, JSON, or Document format.
- **Benchmarks**: Compare model performance (Latency, Throughput, Accuracy).
- **Modular Backend**: FastAPI-based architecture designed for scalability and easy model integration.

## Prerequisites

- **Python 3.10+**
- **Node.js 18+**
- **Redis**: Required for the Pipeline service.
- **Ollama**: Must be installed and running.
  - `ollama pull deepseek-ocr:latest` (or your preferred model)
  - `ollama pull qwen3-vl:8b`

## Setup & Installation

### 1. Core Backend (Port 8000)

Location: `g:\_era\vllm-ocr\backend`

1.  **Navigate to directory**:
    ```powershell
    cd backend
    ```
2.  **Create Virtual Environment**:
    ```powershell
    py -m venv .venv
    ```
3.  **Activate Virtual Environment**:
    ```powershell
    .\.venv\Scripts\activate
    ```
4.  **Install Dependencies**:
    ```powershell
    pip install -r requirements.txt
    ```
5.  **Run Server**:
    ```powershell
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    ```
    Server runs at `http://localhost:8000`.

### 2. Backend Pipeline (Port 8001)

Location: `g:\_era\vllm-ocr\backend-pipeline`

1.  **Navigate to directory**:
    ```powershell
    cd backend-pipeline
    ```
2.  **Create Virtual Environment**:
    ```powershell
    py -m venv .venv
    ```
3.  **Activate Virtual Environment**:
    ```powershell
    .\.venv\Scripts\activate
    ```
4.  **Install Dependencies**:
    ```powershell
    pip install -r requirements.txt
    ```
5.  **Run Server**:
    ```powershell
    uvicorn backend_pipeline.main:app --app-dir src --host 0.0.0.0 --port 8001 --reload
    ```
    Server runs at `http://localhost:8001`.

### 3. Frontend (Port 3000)

Location: `g:\_era\vllm-ocr\frontend`

1.  **Navigate to directory**:
    ```powershell
    cd frontend
    ```
2.  **Install Dependencies**:
    ```powershell
    npm install
    ```
3.  **Run Development Server**:
    ```powershell
    npm run dev
    ```
    App runs at `http://localhost:3000`.

## Architecture

- **Frontend**: Next.js 14 (App Router), Tailwind CSS, Framer Motion.
- **Backend**: FastAPI, PyTorch, Ollama Python Client.
- **Pipeline**: Redis Streams, Worker Process, Advanced Preprocessing.
- **Models**: Pluggable architecture supporting Ollama and Hugging Face models.

## Adding New Models

To add a new model, implement the `BaseOCRModel` interface in `backend/app/models/` and register it in `backend/app/models/manager.py`.

```python
# Example Registration
manager.register_model(OllamaAdapter("my-finetuned-model"))
```
