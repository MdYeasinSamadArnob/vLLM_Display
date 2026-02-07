import httpx
import base64
import logging
import json
from app.models.base import BaseOCRModel, OCRResult

logger = logging.getLogger(__name__)

class VLLMAdapter(BaseOCRModel):
    def __init__(self, model_name: str, base_url: str):
        self._model_name = model_name
        self.base_url = base_url.rstrip("/")
        
    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def provider(self) -> str:
        return "vllm"

    async def load(self) -> None:
        # VLLM models are usually pre-loaded on the server
        pass

    async def unload(self) -> None:
        pass

    async def process_image(self, image_path: str, prompt: str = None, template: str = None) -> OCRResult:
        # Read and encode image
        with open(image_path, "rb") as f:
            image_bytes = f.read()
            encoded_image = base64.b64encode(image_bytes).decode('utf-8')

        # Construct Prompt
        final_prompt = prompt or "Extract all text from this image line by line."
        if template:
             final_prompt += f"\n\nExtract the data according to this JSON schema:\n{template}\nReturn ONLY valid JSON code."

        payload = {
            "model": self._model_name,
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}},
                    {"type": "text", "text": final_prompt}
                ]
            }],
            "max_tokens": 4096,
            "temperature": 0.1
        }

        url = f"{self.base_url}/v1/chat/completions"
        headers = {"Content-Type": "application/json"}
        
        logger.info(f"Calling VLLM at {url} for model {self._model_name}")

        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                return OCRResult(
                    text=content,
                    format="json" if template else "text",
                    metadata={"model": self._model_name, "provider": "vllm"}
                )
            except Exception as e:
                logger.error(f"VLLM Request Failed: {e}")
                # Try to give more context if it's an HTTP status error
                if isinstance(e, httpx.HTTPStatusError):
                     logger.error(f"Response: {e.response.text}")
                raise e
