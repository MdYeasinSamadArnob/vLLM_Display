
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from .models import OCRResponse
from ..queue.redis_streams import enqueue_job
from ..storage.results_store import get_result
import uuid
import base64
import json

router = APIRouter()

@router.get("/v1/ocr/results/{job_id}")
async def get_job_result(job_id: str):
    """
    Get job result.
    """
    result = get_result(job_id)
    if not result:
        # Check if job exists in queue or is processing?
        # For now just return 404 or specific status
        return {"status": "processing", "result": None}
    
    return {"status": "completed", "result": result}

@router.post("/v1/ocr/schema", response_model=OCRResponse)
async def schema_ocr(
    file: UploadFile = File(...),
    schema: str = Form(None) # JSON string
):
    """
    Submit an OCR job.
    """
    job_id = str(uuid.uuid4())
    
    # Read file
    file_bytes = await file.read()
    
    # Parse schema if provided
    schema_dict = {}
    if schema:
        try:
            schema_dict = json.loads(schema)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON in schema")

    # Encode image to base64 for transport in JSON job
    image_b64 = base64.b64encode(file_bytes).decode('utf-8')

    job = {
        "job_id": job_id,
        "mode": "schema" if schema_dict else "text",
        "schema": schema_dict,
        "filename": file.filename,
        "image_bytes": image_b64
    }

    await enqueue_job(job)

    return OCRResponse(job_id=job_id, status="queued")
