from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.models.manager import manager
from app.core.config import settings
from app.utils.image_processing import preprocess_image
import shutil
import os
import uuid
import time

router = APIRouter()

@router.post("/process")
async def process_ocr(
    file: UploadFile = File(...),
    model_name: str = Form(None),
    prompt: str = Form(None),
    template: str = Form(None)
):
    # Validate file type
    if file.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Only JPEG, PNG, and WebP are supported.")

    # 1. Save file
    file_ext = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{file_ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
        
    # 2. Get Model
    target_model = model_name if model_name else manager._active_model_name
    if not target_model:
        # Default to first available if none active
        available = manager.list_models()
        if available:
            target_model = available[0]["name"]
        else:
            raise HTTPException(status_code=500, detail="No models available")
            
    try:
        model = await manager.get_model(target_model)
        
        # 3. Preprocess Image
        processed_path = preprocess_image(file_path)

        # 4. Process
        start_time = time.time()
        result = await model.process_image(processed_path, prompt, template)
        end_time = time.time()
        
        # Add extra timing info
        result.metadata["api_process_time"] = end_time - start_time
        
        return result
        
    except Exception as e:
        # Clean up file on error
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Optional: Clean up file after successful processing if storage is not needed
        # For now, we keep it for debugging or future reference
        pass
