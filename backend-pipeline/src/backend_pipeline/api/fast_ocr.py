
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional, Literal
import logging
import time
import json
from pydantic import BaseModel, Field
from backend_pipeline.workers.pipeline import process_image_core

logger = logging.getLogger(__name__)

router = APIRouter()

# Schema Definitions
class NIDFrontSchema(BaseModel):
    name: str = Field(..., description="Full Name in English")
    name_bn: str = Field(..., description="Full Name in Bangla")
    father_name: str = Field(..., description="Father's Name")
    mother_name: str = Field(..., description="Mother's Name")
    dob: str = Field(..., description="Date of Birth (YYYY-MM-DD)")
    nid_no: str = Field(..., description="NID Number (10, 13, or 17 digits)")

class NIDBackSchema(BaseModel):
    address_bn: str = Field(..., description="Address in Bangla (Thikana)")
    blood_group: str = Field(..., description="Blood Group")
    place_of_birth: str = Field(..., description="Place of Birth")
    issue_date: str = Field(..., description="Issue Date")
    mrz_line1: str = Field(..., description="MRZ Line 1")
    mrz_line2: str = Field(..., description="MRZ Line 2")
    mrz_line3: str = Field(..., description="MRZ Line 3")

# Map to dicts for schema engine
NID_FRONT_SCHEMA_DICT = {
    "name": "Full Name in English",
    "name_bn": "Full Name in Bangla",
    "father_name": "Father's Name",
    "mother_name": "Mother's Name",
    "dob": "Date of Birth (YYYY-MM-DD)",
    "nid_no": "NID Number (10, 13, or 17 digits)"
}

NID_BACK_SCHEMA_DICT = {
    "address_bn": "Address in Bangla (Thikana)",
    "blood_group": "Blood Group",
    "place_of_birth": "Place of Birth",
    "issue_date": "Issue Date",
    "mrz_line1": "MRZ Line 1",
    "mrz_line2": "MRZ Line 2",
    "mrz_line3": "MRZ Line 3"
}

@router.post("/direct")
async def ocr_direct(
    file: UploadFile = File(...),
    type: Literal["nid_front", "nid_back"] = Form(..., description="Type of document: 'nid_front' or 'nid_back'")
):
    """
    High-throughput independent API for OCR.
    Bypasses Redis stream and processes immediately.
    """
    start_time = time.time()
    job_id = f"direct-{time.time_ns()}"
    
    logger.info(f"Received direct OCR request [{job_id}] for type: {type}")
    
    try:
        # Read file
        image_bytes = await file.read()
        
        # Determine schema
        if type == "nid_front":
            schema = NID_FRONT_SCHEMA_DICT
        elif type == "nid_back":
            schema = NID_BACK_SCHEMA_DICT
        else:
            raise HTTPException(status_code=400, detail="Invalid type. must be 'nid_front' or 'nid_back'")
            
        # Process
        result = await process_image_core(image_bytes, mode="schema", schema=schema, job_id=job_id)
        
        # Calculate duration
        duration = (time.time() - start_time) * 1000
        logger.info(f"Direct OCR request [{job_id}] completed in {duration:.2f}ms")
        
        return {
            "status": "success",
            "job_id": job_id,
            "duration_ms": duration,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Error in direct OCR [{job_id}]: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
