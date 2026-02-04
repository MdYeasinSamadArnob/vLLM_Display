from fastapi import APIRouter, HTTPException
from typing import List, Dict
from app.models.manager import manager
from pydantic import BaseModel

router = APIRouter()

class ModelInfo(BaseModel):
    name: str
    provider: str
    active: bool

class SetActiveModelRequest(BaseModel):
    name: str

@router.get("", response_model=List[ModelInfo])
async def list_models():
    return manager.list_models()

@router.post("/active")
async def set_active_model(request: SetActiveModelRequest):
    try:
        await manager.set_active_model(request.name)
        return {"message": f"Active model set to {request.name}"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
