
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
        
        # 6. Verification & Correction (Always-On Judge)
        # User Instruction: Always call judge to verify/fix names (spelling, spacing, typos).
        # Constraint: Do NOT change DOB or NID No unless critical. Trust Scribe for numbers.
        
        logger.info("Running Qwen3-VL Judge for Verification...")
        try:
            success, encoded_norm = cv2.imencode('.jpg', image)
            if success:
                import json
                scribe_json = json.dumps(final_result, ensure_ascii=False)
                
                # Dynamic Prompt Generation based on Schema
                schema_keys = list(final_result.keys())
                
                # Base Prompt
                verification_prompt = (
                    f"You are a professional OCR Proofreader. \n"
                    f"Here is the raw extraction from a Scribe: {scribe_json}\n"
                    f"Task:\n"
                )
                
                # Dynamic Rules
                if "name" in schema_keys or "name_bn" in schema_keys:
                    verification_prompt += f"1. Verify and fix spelling, spacing, and typos in 'name' (English). For 'name_bn' (Bangla), extract it from the image if missing or invalid, as the Scribe may not capture Bangla.\n"
                
                if "address_bn" in schema_keys:
                    verification_prompt += f"3. Extract or Verify the Bangla Address ('address_bn'). Ensure it matches the image text exactly.\n"
                
                if "place_of_birth" in schema_keys:
                    verification_prompt += f"4. Verify 'place_of_birth'.\n"

                if "mrz_line1" in schema_keys or "mrz_line2" in schema_keys or "mrz_line3" in schema_keys:
                     verification_prompt += f"5. Extract the MRZ (Machine Readable Zone) lines at the bottom of the card into 'mrz_line1', 'mrz_line2', 'mrz_line3'. They consist of uppercase letters, numbers, and '<'. Ensure strict accuracy.\n"

                # Critical Preservation Rules
                verification_prompt += f"6. CRITICAL: Do NOT change 'dob', 'nid_no', 'issue_date', 'blood_group' unless they are visually contradictory to the image. Trust the Scribe's numbers/dates.\n"
                
                # Return Format
                verification_prompt += f"7. Return the corrected JSON object ONLY. No markdown."

                # Note: We rely on call_vllm logic to pick up OLLAMA_URL for this model name
                qwen_result = await call_vllm(
                    encoded_norm.tobytes(), 
                    model_name="qwen3-vl:8b-instruct",
                    prompt_text=verification_prompt
                )
                
                if 'choices' in qwen_result and len(qwen_result['choices']) > 0:
                    qwen_text = qwen_result['choices'][0]['message']['content']
                    logger.info(f"Qwen Verification Output: {qwen_text[:200]}...")
                    
                    import re
                    try:
                        # Try to parse JSON
                        json_match = re.search(r'\{.*\}', qwen_text, re.DOTALL)
                        if json_match:
                            qwen_verified = json.loads(json_match.group(0))
                            
                            # Merge/Update logic
                            # We blindly trust the Judge for names/text, but we double-check logic for numbers.
                            
                            for k, v in qwen_verified.items():
                                # Safety: Don't overwrite existing numeric/date fields with empty or null if Judge failed
                                # Added issue_date and blood_group to protected fields
                                if k in ['dob', 'nid_no', 'issue_date', 'blood_group'] and not v:
                                    continue
                                
                                # Text fields: Update unconditionally
                                if k in ['name', 'name_bn', 'address_bn', 'place_of_birth', 'mrz_line1', 'mrz_line2', 'mrz_line3']:
                                    if v:
                                        final_result[k] = v
                                        logger.info(f"Judge corrected {k}: {v}")
                                else:
                                    # For protected fields, update only if missing in Scribe
                                    if not final_result.get(k) and v:
                                        final_result[k] = v
                                        logger.info(f"Judge filled missing {k}: {v}")
                                    # If Scribe has it, we KEEP Scribe's value
                        else:
                            logger.warning("Judge output did not contain valid JSON.")
                    except Exception as parse_e:
                        logger.error(f"Failed to parse Judge output: {parse_e}")
        except Exception as e:
            logger.error(f"Qwen Judge failed: {e}")
        
    # 6. Save Result
    save_result(job_id, final_result)
    logger.info(f"Job {job_id} completed")
