from fastapi import APIRouter
from typing import List, Dict, Any

router = APIRouter()

# Mock benchmark data for now, or we can store real runs
BENCHMARKS = [
    {
        "model": "deepseek-ocr:latest",
        "accuracy": "98.5%",
        "avg_latency": "1.2s",
        "throughput": "50 img/min",
        "memory_usage": "4GB"
    },
    {
        "model": "qwen3-vl:8b",
        "accuracy": "97.8%",
        "avg_latency": "0.8s",
        "throughput": "70 img/min",
        "memory_usage": "3.5GB"
    }
]

@router.get("")
async def get_benchmarks():
    return BENCHMARKS
