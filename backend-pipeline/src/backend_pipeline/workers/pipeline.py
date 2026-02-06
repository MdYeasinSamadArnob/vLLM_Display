
import logging
import cv2
import numpy as np
from ..preprocess.normalize import normalize
from ..preprocess.multiview import generate_views
from ..ocr.vllm_client import call_vllm
from ..postprocess.consensus import consensus
from ..postprocess.schema_engine import run_schema_pipeline
from ..storage.results_store import save_result
import asyncio

logger = logging.getLogger(__name__)

async def process_job(job: dict):
    """
    Process a single OCR job.
    1. Preprocess
    2. Generate Views
    3. Run OCR on views
    4. Consensus
    5. Schema/Text Extraction
    6. Save Result
    """
    job_id = job.get("job_id")
    logger.info(f"Processing job {job_id}")
    
    # Decode image
    # Assuming job["image_bytes"] is passed as base64 string or bytes
    # In redis_streams.py we decided to pass it through. 
    # If it came from API, it might be bytes. 
    # But JSON serialization in Redis means it likely needs to be base64 string if inside JSON.
    # Let's assume it's base64 encoded string in the job dict.
    
    import base64
    image_data = job.get("image_bytes")
    if isinstance(image_data, str):
        image_bytes = base64.b64decode(image_data)
    else:
        image_bytes = image_data
        
    # 1. Preprocess
    image = normalize(image_bytes)
    
    # 2. Generate Views
    views = generate_views(image)
    
    # 3. Run OCR on views (Parallelize if possible)
    # For now, sequential await
    ocr_outputs = []
    for view_img, off_x, off_y in views:
        # Encode view back to bytes for vLLM client
        success, encoded_view = cv2.imencode('.jpg', view_img)
        if success:
            try:
                result = await call_vllm(encoded_view.tobytes())
                # Add offsets to result metadata or structure so consensus knows
                # Assuming result is a dict, we wrap it
                ocr_outputs.append({
                    "result": result,
                    "offset_x": off_x,
                    "offset_y": off_y
                })
            except Exception as e:
                logger.error(f"OCR failed for a view: {e}")
    
    # 4. Consensus
    merged = consensus(ocr_outputs)
    
    # 5. Postprocess
    mode = job.get("mode", "text")
    if mode == "text":
        # Just return the text from consensus
        final_result = {"text": merged}
    else:
        schema = job.get("schema", {})
        final_result = run_schema_pipeline(schema, merged, image)
        
        # Fallback Logic: If name_bn is missing, try Qwen3-VL
        if "name_bn" in schema and not final_result.get("name_bn"):
            logger.info("Bangla text missing. Attempting Qwen3-VL fallback.")
            try:
                success, encoded_norm = cv2.imencode('.jpg', image)
                if success:
                    # Note: We rely on call_vllm logic to pick up OLLAMA_URL for this model name
                    qwen_result = await call_vllm(
                        encoded_norm.tobytes(), 
                        model_name="qwen3-vl:8b",
                        prompt_text="Extract the following fields from this Bangladesh NID card: Name (English), Name (Bangla), Father's Name, Mother's Name, Date of Birth, NID No. Return ONLY a JSON object with keys: name, name_bn, father_name, mother_name, dob, nid_no. Ensure Bangla text is transcribed exactly. No markdown, no explanations."
                    )
                    
                    if 'choices' in qwen_result and len(qwen_result['choices']) > 0:
                        qwen_text = qwen_result['choices'][0]['message']['content']
                        logger.info(f"Qwen Fallback Output: {qwen_text[:200]}...")
                        
                        import json
                        import re
                        try:
                            # Try to parse JSON
                            json_match = re.search(r'\{.*\}', qwen_text, re.DOTALL)
                            if json_match:
                                qwen_extracted = json.loads(json_match.group(0))
                            else:
                                # Fallback to schema engine on Qwen text
                                qwen_extracted = run_schema_pipeline(schema, qwen_text, image)
                                
                            # Merge into final result
                            for k, v in qwen_extracted.items():
                                if not final_result.get(k) and v:
                                    final_result[k] = v
                                    logger.info(f"Updated {k} from Qwen result")
                        except Exception as parse_e:
                            logger.error(f"Failed to parse Qwen output: {parse_e}")
            except Exception as e:
                logger.error(f"Qwen fallback failed: {e}")
        
    # 6. Save Result
    save_result(job_id, final_result)
    logger.info(f"Job {job_id} completed")
