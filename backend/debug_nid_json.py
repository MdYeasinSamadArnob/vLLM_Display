import asyncio
import os
import json
from dotenv import load_dotenv
load_dotenv()

from app.core.config import settings
from app.models.ollama_adapter import OllamaAdapter
from app.utils.image_processing import preprocess_image

import traceback

async def test_nid_json():
    print(f"OLLAMA_BASE_URL: {settings.OLLAMA_BASE_URL}")
    
    # List available models
    try:
        import ollama
        client = ollama.AsyncClient(host=settings.OLLAMA_BASE_URL)
        models_resp = await client.list()
        print("\nAvailable Models on Remote Server:")
        for m in models_resp['models']:
            # Try 'name' or 'model' key
            model_name = m.get('name') or m.get('model')
            print(f"- {model_name}")
        print("----------------------------------\n")
    except Exception as e:
        print(f"Could not list models: {e}")

    adapter = OllamaAdapter("deepseek-ocr:latest")
    image_path = os.path.join(os.path.dirname(__file__), "sample-images", "nid-test.png")
    
    # Preprocess
    processed_path = preprocess_image(image_path)
    print(f"Testing NID JSON Extraction on: {processed_path}")
    
    # User provided template
    json_template = """
 { 
   "document": { 
     "type": "NATIONAL_ID", 
     "country": "BD", 
     "issuing_authority": "Government of the People's Republic of Bangladesh", 
     "card_title_en": "NATIONAL ID CARD", 
     "card_title_bn": "জাতীয় পরিচয়পত্র" 
   }, 
   "holder": { 
     "name": { 
       "en": "", 
       "bn": "" 
     }, 
     "father_name": { 
       "en": "", 
       "bn": "" 
     }, 
     "mother_name": { 
       "en": "", 
       "bn": "" 
     }, 
     "date_of_birth": "", 
     "gender": "", 
     "nid_number": "", 
     "photo_present": false 
   }, 
   "address": { 
     "present_address": "", 
     "permanent_address": "" 
   }, 
   "extraction": { 
     "source": "image", 
     "ocr_engine": "", 
     "language_detected": ["bn", "en"], 
     "fields_extracted": [ 
       "name", 
       "father_name", 
       "mother_name", 
       "date_of_birth", 
       "nid_number" 
     ], 
     "confidence_scores": { 
       "name": 0.0, 
       "father_name": 0.0, 
       "mother_name": 0.0, 
       "date_of_birth": 0.0, 
       "nid_number": 0.0 
     } 
   }, 
   "validation": { 
     "nid_format_valid": false, 
     "dob_format_valid": false, 
     "mandatory_fields_present": false 
   }, 
   "timestamps": { 
     "extracted_at": "", 
     "verified_at": "" 
   } 
 }
    """

    try:
        print("\n--- Test: Complex JSON Template ---")
        result = await adapter.process_image(processed_path, template=json_template)
        
        print("Vision Pass Text (Intermediate):")
        print(result.metadata.get('vision_text', 'N/A'))
        print("\nFinal JSON Result:")
        print(result.text)
    except Exception as e:
        print(f"Error caught: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_nid_json())
