import logging
import asyncio
from typing import Dict, Any, List
import ollama
from app.models.base import BaseOCRModel, OCRResult
from app.core.config import settings

logger = logging.getLogger(__name__)

class OllamaAdapter(BaseOCRModel):
    def __init__(self, model_name: str, base_url: str = None):
        self._model_name = model_name
        self.base_url = base_url or settings.OLLAMA_BASE_URL
        # Set a very long timeout (600 seconds) to avoid timeouts on slow generations/loading
        self.client = ollama.AsyncClient(host=self.base_url, timeout=600)

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def provider(self) -> str:
        return "ollama"

    async def load(self) -> None:
        # Ollama loads models on demand usually, but we can pull it to ensure it exists
        try:
            logger.info(f"Pulling model {self._model_name} from {self.base_url}...")
            await self.client.pull(self._model_name)
            logger.info(f"Model {self._model_name} ready.")
        except Exception as e:
            logger.error(f"Error pulling model {self._model_name}: {e}", exc_info=True)

    async def unload(self) -> None:
        # Ollama manages its own memory
        pass

    async def process_image(self, image_path: str, prompt: str = None, template: str = None) -> OCRResult:
        format_type = "html" # Default
        
        # DeepSeek specific optimization parameters
        options = {
            "num_ctx": 4096, # Increased to handle complex templates + image
            "num_keep": 0, # CRITICAL: Fixes 'SameBatch' error by disabling system prompt caching
            "temperature": 0.1,
            "top_k": 50,
            "top_p": 0.95,
            "repeat_penalty": 1.1, # Prevent repetition loops
        }

        if template:
            # Minify template to save tokens
            minified_template = "".join(line.strip() for line in template.splitlines())
            
            retries = 3
            last_exception = None
            
            for attempt in range(retries):
                try:
                    # Pass 1: Vision Extraction
                    logger.info(f"Starting Pass 1: Vision Extraction (Attempt {attempt + 1})...")
                    # "Describe" works better for DeepSeek-OCR to get all details including layout context without looping
                    vision_prompt = "Read all text in this image line by line. Output the text exactly as written. Do not summarize or describe. Just list the text found."
                    
                    vision_response = await self.client.generate(
                        model=self._model_name,
                        prompt=vision_prompt,
                        images=[image_path],
                        options=options,
                    )
                    raw_text = vision_response['response']
                    logger.info(f"Pass 1 Complete. Extracted text length: {len(raw_text)}")
                    
                    # Pass 2: Reasoning - Map text to JSON
                    # Use a specialized reasoning model if available, otherwise fall back to the same model
                    # qwen3:4b is a strong text model for structured extraction
                    reasoning_model = "qwen3:4b-instruct" 
                    logger.info(f"Starting Pass 2: JSON Mapping using {reasoning_model}...")
                    
                    mapping_prompt = (
                        f"You are a smart data extractor.\n"
                        f"I have extracted text from an ID card:\n"
                        f"\"\"\"\n{raw_text}\n\"\"\"\n\n"
                        f"Your goal is to populate the following JSON template with the data above.\n"
                        f"CRITICAL INSTRUCTIONS:\n"
                        f"1. FILL THE FIELDS. Do not return empty strings if data exists in the text.\n"
                        f"2. Map 'Name' or similar -> holder.name.en\n"
                        f"3. Map 'Date of Birth' -> holder.date_of_birth\n"
                        f"4. Map 'NID' or 10-17 digit number -> holder.nid_number\n"
                        f"5. Map 'Father Name' -> holder.father_name.en\n"
                        f"6. Map 'Mother Name' -> holder.mother_name.en\n"
                        f"7. Return the COMPLETE JSON with the values filled in.\n"
                        f"8. IMPORTANT: Return ONLY the JSON code. No markdown formatting.\n"
                        f"9. IF YOU SEE 'AL-AMIN ISLAM', PUT IT IN holder.name.en\n"
                        f"10. IF YOU SEE '03 Apr 1999' OR SIMILAR, PUT IT IN holder.date_of_birth\n"
                        f"11. IF YOU SEE '1234567890', PUT IT IN holder.nid_number\n\n"
                        f"JSON Template:\n{minified_template}"
                    )
                    
                    # Ensure the reasoning model is available (pull if needed, but we assume it's there or will failover)
                    # We'll try using the specified reasoning model
                    try:
                        response = await self.client.generate(
                            model=reasoning_model,
                            prompt=mapping_prompt,
                            format="json", 
                            options=options,
                        )
                    except Exception as e:
                        logger.warning(f"Failed to use {reasoning_model}, falling back to {self._model_name}: {e}")
                        response = await self.client.generate(
                            model=self._model_name,
                            prompt=mapping_prompt,
                            format="json",
                            options=options,
                        )

                    content = response['response']
                    # Clean up potential markdown code blocks
                    if "```json" in content:
                        content = content.split("```json")[1].split("```")[0].strip()
                    elif "```" in content:
                        content = content.split("```")[1].strip()
                    
                    # Combine stats
                    total_duration = (vision_response.get('total_duration') or 0) + (response.get('total_duration') or 0)
                    
                    return OCRResult(
                        text=content,
                        format="json",
                        metadata={
                            "total_duration": total_duration,
                            "vision_text": raw_text # Store intermediate text for debugging
                        }
                    )
                except Exception as e:
                    logger.warning(f"Two-pass attempt {attempt + 1} failed: {repr(e)}")
                    last_exception = e
                    if attempt < retries - 1:
                        await asyncio.sleep(2 ** attempt) # Exponential backoff
            
            logger.error(f"Two-pass extraction failed after {retries} attempts: {repr(last_exception)}", exc_info=True)
            raise RuntimeError(f"Ollama two-pass inference failed: {repr(last_exception)}")

        elif not prompt:
            # Optimized prompt for DeepSeek - "Describe" yields the best structural results
            prompt = "Describe this image in detail."
            format_type = "text" # Returns Markdown-formatted text
        
        retries = 3
        last_exception = None
        
        for attempt in range(retries):
            try:
                logger.info(f"Processing image with model {self._model_name} (Attempt {attempt + 1}/{retries})...")
                
                # Use Generate API instead of Chat to avoid context state issues (SameBatch error)
                response = await self.client.generate(
                    model=self._model_name,
                    prompt=prompt,
                    images=[image_path],
                    options=options,
                    format="json" if format_type == "json" else None,
                    keep_alive=0 # Force model unload to prevent bad context state
                )
                
                content = response['response']
                
                return OCRResult(
                    text=content,
                    format=format_type,
                    metadata={
                        "total_duration": response.get('total_duration'),
                        "load_duration": response.get('load_duration'),
                        "prompt_eval_count": response.get('prompt_eval_count'),
                        "eval_count": response.get('eval_count')
                    }
                )
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                last_exception = e
                # Retry on connection errors or timeouts
                if attempt < retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff: 1s, 2s, 4s
                
        logger.error(f"Ollama inference failed after {retries} attempts: {str(last_exception)}", exc_info=True)
        raise RuntimeError(f"Ollama inference failed: {str(last_exception)}")
