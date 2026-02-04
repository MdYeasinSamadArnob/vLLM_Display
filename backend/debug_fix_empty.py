import asyncio
import os
import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models.ollama_adapter import OllamaAdapter
from app.core.config import settings

async def debug_empty_response():
    print(f"Ollama URL: {settings.OLLAMA_BASE_URL}")
    
    model_name = "deepseek-ocr:latest"
    adapter = OllamaAdapter(model_name)
    
    image_path = r"g:\_era\vllm-ocr\backend\sample-images\test-ocr.PNG"
    
    if not os.path.exists(image_path):
        print(f"Image not found at {image_path}")
        return

    print(f"Processing image: {image_path}")
    
    # Test 1: Standard HTML extraction (the default path)
    print("\n--- Test 1: HTML Extraction (Default) ---")
    try:
        # Intentionally not passing prompt/template to trigger default logic
        result = await adapter.process_image(image_path)
        print(f"Result Format: {result.format}")
        print(f"Raw Text Length: {len(result.text)}")
        print("Raw Text Content (First 500 chars):")
        print(result.text[:500])
        print("...")
        
        if not result.text.strip():
            print("!!! WARNING: Result text is empty or whitespace only !!!")
            
    except Exception as e:
        print(f"Error in Test 1: {e}")

    # Test 2: With explicit prompt
    print("\n--- Test 2: Explicit Simple Prompt ---")
    try:
        prompt = "OCR this image. Return markdown."
        result = await adapter.process_image(image_path, prompt=prompt)
        print(f"Result Format: {result.format}")
        print(f"Raw Text Length: {len(result.text)}")
        print(result.text[:200])
    except Exception as e:
        print(f"Error in Test 2: {e}")

    # Test 3: Simpler HTML Prompt
    print("\n--- Test 3: Simpler HTML Prompt ---")
    try:
        prompt = "Convert the text and layout in this image into a simple HTML document."
        result = await adapter.process_image(image_path, prompt=prompt)
        print(f"Raw Text Length: {len(result.text)}")
        print(result.text[:200])
    except Exception as e:
        print(f"Error in Test 3: {e}")

    # Test 4: Structured HTML Prompt
    print("\n--- Test 4: Structured HTML Prompt ---")
    try:
        prompt = "Extract text from image. Output valid HTML with inline CSS for styling."
        result = await adapter.process_image(image_path, prompt=prompt)
        print(f"Raw Text Length: {len(result.text)}")
        print(result.text[:200])
    except Exception as e:
        print(f"Error in Test 4: {e}")
        
if __name__ == "__main__":
    asyncio.run(debug_empty_response())
