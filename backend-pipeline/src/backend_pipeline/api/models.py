
from pydantic import BaseModel
from typing import Optional, Dict, Any

class OCRRequest(BaseModel):
    mode: str = "text" # "text" or "schema"
    schema_definition: Optional[Dict[str, Any]] = None

class OCRResponse(BaseModel):
    job_id: str
    status: str
