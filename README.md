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
- **Ollama**: Must be installed and running.
  - `ollama pull deepseek-ocr:latest` (or your preferred model)
  - `ollama pull qwen3-vl:8b`

## Setup & Installation

### Backend

1. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```
2. Create and activate virtual environment:
   ```bash
   # Windows
   py -m venv venv
   .\venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the server:
   ```bash
   uvicorn app.main:app --reload
   ```
   Server runs at `http://localhost:8000`.

### Frontend

1. Navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```
   App runs at `http://localhost:3000`.

## Architecture

- **Frontend**: Next.js 14 (App Router), Tailwind CSS, Framer Motion.
- **Backend**: FastAPI, PyTorch, Ollama Python Client.
- **Models**: Pluggable architecture supporting Ollama and Hugging Face models.

## Adding New Models

To add a new model, implement the `BaseOCRModel` interface in `backend/app/models/` and register it in `backend/app/models/manager.py`.

```python
# Example Registration
manager.register_model(OllamaAdapter("my-finetuned-model"))
```
