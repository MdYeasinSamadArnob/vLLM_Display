
import httpx
import base64
import os
import logging
import json
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

VLLM_URL = os.getenv("VLLM_URL", os.getenv("VLLM_OCR_URL", "http://10.11.200.99:8091/"))
OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://10.11.200.109:11434")

DEFAULT_MODEL = "tencent/HunyuanOCR"

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def call_vllm(image_bytes: bytes, model_name: str = DEFAULT_MODEL, api_url: str = None, prompt_text: str = None) -> dict:
    """
    Call the vLLM/Ollama service for OCR.
    """
    # Resolve URLs dynamically to support late env loading
    current_ollama_url = os.getenv("OLLAMA_BASE_URL", "http://10.11.200.109:11434")
    current_vllm_url = os.getenv("VLLM_URL", os.getenv("VLLM_OCR_URL", "http://10.11.200.99:8091/"))

    # Determine API URL
    if api_url:
        base_url = api_url
    # elif model_name == "qwen3-vl:8b" and OLLAMA_URL:
    elif model_name == "qwen3-vl:8b-instruct" and current_ollama_url:
        base_url = current_ollama_url
    else:
        base_url = current_vllm_url

    # Encode image to base64
    encoded_image = base64.b64encode(image_bytes).decode('utf-8')
    
    if prompt_text is None:
        prompt_text = "Extract only English and Bangla text, Numbers, and Dates from this Bangladesh National ID card. Output the text line by line."

    payload = {
        "model": model_name,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "image_url", 
                 "image_url": {
                    "url": f"data:image/png;base64,{encoded_image}"
                 }},
                {"type": "text", "text": prompt_text}
            ]
        }],
        "max_tokens": 4096,
        "temperature": 0.0,
    }

    # Add repetition_penalty only if not using Ollama (or check if Ollama supports it via options)
    # We assume if the URL is OLLAMA_URL, we skip it or be careful.
    is_ollama = (base_url == OLLAMA_URL)
    if not is_ollama:
        payload["repetition_penalty"] = 1.05

    headers = {
        "Authorization": "Bearer EMPTY"
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        url = f"{base_url.rstrip('/')}/v1/chat/completions"
        logger.info(f"Calling OCR service at {url} with model {model_name}")
        
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()
        logger.info(f"vLLM Response: {json.dumps(result)}")
        return result
