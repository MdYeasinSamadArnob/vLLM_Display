
import asyncio
import logging
import os
import sys
import json
import cv2
from dotenv import load_dotenv

# Setup paths
# We assume we are running from project root or backend-pipeline root
# Try to find 'backend-pipeline/src'
base_dir = os.getcwd()
if os.path.basename(base_dir) != "backend-pipeline":
    src_path = os.path.join(base_dir, "backend-pipeline", "src")
else:
    src_path = os.path.join(base_dir, "src")

print(f"Adding to path: {src_path}")
sys.path.append(src_path)

# Load env
env_path = r"g:\_era\vllm-ocr\backend\.env"
if os.path.exists(env_path):
    load_dotenv(env_path)
    print(f"Loaded env from {env_path}")
else:
    load_dotenv()
    print("Loaded env from default location")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from backend_pipeline.ocr.vllm_client import call_vllm
from backend_pipeline.postprocess.consensus import consensus
from backend_pipeline.postprocess.schema_engine import run_schema_pipeline
from backend_pipeline.preprocess.normalize import normalize
from backend_pipeline.preprocess.multiview import generate_views

async def test_run():
    image_path = r"g:\_era\vllm-ocr\backend\sample-images\nid-test.png"
    if not os.path.exists(image_path):
        print(f"Image not found at {image_path}")
        return

    print(f"--- Testing with image: {image_path} ---")
    
    # Read image
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    # 1. Preprocess
    print("\n[Step 1] Normalizing...")
    image = normalize(image_bytes)

    # 2. Generate Views
    print("\n[Step 2] Generating Views...")
    views = generate_views(image)
    print(f"Generated {len(views)} views")

    # 3. OCR on Views
    print("\n[Step 3] Running OCR on views...")
    ocr_outputs = []
    for i, (view_img, off_x, off_y) in enumerate(views):
        print(f"  - View {i}: size={view_img.shape}, offset=({off_x}, {off_y})")
        
        # Encode view
        success, encoded_view = cv2.imencode('.jpg', view_img)
        if not success:
            print(f"    Failed to encode view {i}")
            continue
            
        try:
            # We pass bytes to call_vllm
            # Using GLM-OCR as requested
            result = await call_vllm(encoded_view.tobytes(), model_name="glm-ocr:latest")
            print(f"    Result: {json.dumps(result)[:100]}...") # Truncate for readability
            
            ocr_outputs.append({
                "result": result,
                "offset_x": off_x,
                "offset_y": off_y
            })
        except Exception as e:
            print(f"    OCR Failed for view {i}: {e}")

    # 4. Consensus
    print("\n[Step 4] Running Consensus...")
    merged_text = consensus(ocr_outputs)
    # print("Merged Text (Repr):", repr(merged_text))
    
    # Dump merged text to file for inspection
    with open("debug_merged_text.txt", "w", encoding="utf-8") as f:
        f.write(merged_text)
    print("Dumped merged text to debug_merged_text.txt")

    # 5. Schema Engine
    print("\n[Step 5] Running Schema Engine...")
    schema = {
        "name": "Name",
        "name_bn": "Name (Bangla)",
        "father_name": "Father's Name",
        "mother_name": "Mother's Name",
        "dob": "Date of Birth",
        "nid_no": "NID No"
    }
    
    final_result = run_schema_pipeline(schema, merged_text, image)
    
    print("\n[Final Result (Initial)]")
    print(json.dumps(final_result, indent=2))

    # Check if Bangla extraction failed
    if not final_result.get("name_bn"):
        print("\n[Fallback] Bangla text not found. Attempting extraction with Qwen3-VL (Ollama)...")
        
        # Encode the normalized image
        success, encoded_norm = cv2.imencode('.jpg', image)
        if success:
            try:
                # Call Qwen
                # Note: We rely on call_vllm logic to pick up OLLAMA_URL for this model name
                qwen_result = await call_vllm(
                    encoded_norm.tobytes(), 
                    model_name="qwen3-vl:8b",
                    prompt_text="Extract the following fields from this Bangladesh NID card: Name (English), Name (Bangla), Father's Name, Mother's Name, Date of Birth, NID No. Return ONLY a JSON object with keys: name, name_bn, father_name, mother_name, dob, nid_no. Ensure Bangla text is transcribed exactly. No markdown, no explanations."
                )
                
                # Extract text
                if 'choices' in qwen_result and len(qwen_result['choices']) > 0:
                    qwen_text = qwen_result['choices'][0]['message']['content']
                    print(f"Qwen Output: {qwen_text}...")
                    
                    # Try to parse JSON directly
                    import re
                    try:
                        # Find JSON block
                        json_match = re.search(r'\{.*\}', qwen_text, re.DOTALL)
                        if json_match:
                            json_str = json_match.group(0)
                            qwen_extracted = json.loads(json_str)
                            print("Qwen JSON Parsed:", json.dumps(qwen_extracted, indent=2))
                        else:
                            # Fallback to schema engine if no JSON found
                            print("No JSON found in Qwen output, using schema engine")
                            qwen_extracted = run_schema_pipeline(schema, qwen_text, image)
                    except Exception as e:
                        print(f"JSON Parsing failed: {e}")
                        qwen_extracted = run_schema_pipeline(schema, qwen_text, image)
                    
                    # Merge into final result
                    for k, v in qwen_extracted.items():
                        if not final_result.get(k) and v:
                            final_result[k] = v
                            print(f"Updated {k} from Qwen result")
                else:
                    print("Qwen returned no choices")
                        
            except Exception as e:
                print(f"Qwen Fallback Failed: {e}")
                import traceback
                traceback.print_exc()

    print("\n[Final Result (Merged)]")
    print(json.dumps(final_result, indent=2))

if __name__ == "__main__":
    asyncio.run(test_run())
