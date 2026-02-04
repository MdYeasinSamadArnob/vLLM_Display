from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class OCRResult(BaseModel):
    text: str
    format: str  # 'plain', 'json', 'markdown'
    metadata: Dict[str, Any] = {}
    bounding_boxes: Optional[List[Dict[str, Any]]] = None  # For polygon visualization

class BaseOCRModel(ABC):
    @abstractmethod
    async def load(self) -> None:
        """Load the model into memory."""
        pass

    @abstractmethod
    async def unload(self) -> None:
        """Unload the model to free resources."""
        pass

    @abstractmethod
    async def process_image(self, image_path: str, prompt: Optional[str] = None, template: Optional[str] = None) -> OCRResult:
        """
        Process an image and return extracted text/data.
        
        Args:
            image_path: Path to the image file.
            prompt: Optional specific prompt to guide the model.
            template: Optional JSON template/schema to structure the output.
        """
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        pass
    
    @property
    @abstractmethod
    def provider(self) -> str:
        """'ollama', 'huggingface', etc."""
        pass
